"""
app/api/v1/executive_summary.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import date, timedelta
import anthropic
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.product import Product
from app.models.demand import DemandRecord
from app.models.forecast import ForecastRecord
from app.models.anomaly import AnomalyRecord

router = APIRouter()


async def _gather_inventory_context(db: AsyncSession) -> dict:
    today = date.today()

    products_result = await db.execute(select(Product))
    products = products_result.scalars().all()

    stockout_products = [p for p in products if p.current_stock == 0]
    critical_products = [p for p in products if 0 < p.current_stock <= (p.reorder_point or 0)]
    healthy_products  = [p for p in products if p.current_stock > (p.reorder_point or 0)]
    total_stock_value = sum((p.current_stock or 0) * (p.unit_cost or 0) for p in products)

    anomaly_result = await db.execute(
        select(AnomalyRecord, Product.name)
        .join(Product, AnomalyRecord.product_id == Product.id)
        .where(AnomalyRecord.date >= today - timedelta(days=14))
        .where(AnomalyRecord.severity.in_(["HIGH", "MEDIUM"]))
        .order_by(desc(AnomalyRecord.date))
        .limit(5)
    )
    recent_anomalies = anomaly_result.all()

    forecast_result = await db.execute(
        select(
            ForecastRecord.product_id,
            Product.name,
            func.sum(ForecastRecord.predicted_quantity).label("total_forecast"),
            func.avg(ForecastRecord.predicted_quantity).label("avg_daily")
        )
        .join(Product, ForecastRecord.product_id == Product.id)
        .where(ForecastRecord.forecast_date >= today)
        .where(ForecastRecord.forecast_date <= today + timedelta(days=30))
        .group_by(ForecastRecord.product_id, Product.name)
        .order_by(desc("total_forecast"))
        .limit(5)
    )
    top_forecasts = forecast_result.all()

    recent_7 = await db.execute(
        select(func.sum(DemandRecord.quantity))
        .where(DemandRecord.date >= today - timedelta(days=7))
    )
    prev_7 = await db.execute(
        select(func.sum(DemandRecord.quantity))
        .where(DemandRecord.date >= today - timedelta(days=14))
        .where(DemandRecord.date < today - timedelta(days=7))
    )

    recent_7_total = recent_7.scalar() or 0
    prev_7_total   = prev_7.scalar() or 1

    demand_trend_pct = round(((recent_7_total - prev_7_total) / prev_7_total) * 100, 1)

    return {
        "total_products":    len(products),
        "stockout_count":    len(stockout_products),
        "critical_count":    len(critical_products),
        "healthy_count":     len(healthy_products),
        "total_stock_value": round(total_stock_value, 2),
        "stockout_names":    [p.name for p in stockout_products],
        "critical_names":    [p.name for p in critical_products],
        "demand_trend_pct":  demand_trend_pct,
        "recent_anomalies":  [
            {
                "product":  row[1],
                "severity": row[0].severity,
                "date":     str(row[0].date),
                "z_score":  round(row[0].z_score or 0, 2)
            }
            for row in recent_anomalies
        ],
        "top_forecasts": [
            {
                "product":   row.name,
                "total_30d": round(row.total_forecast or 0),
                "avg_daily": round(row.avg_daily or 0, 1)
            }
            for row in top_forecasts
        ],
        "generated_date": str(today),
    }


def _build_prompt(ctx: dict) -> str:
    stockouts_text = (
        f"The following products are completely out of stock: {', '.join(ctx['stockout_names'])}."
        if ctx["stockout_names"]
        else "No products are currently out of stock."
    )
    critical_text = (
        f"These products are running critically low: {', '.join(ctx['critical_names'])}."
        if ctx["critical_names"]
        else "No products are in a critical low-stock state."
    )
    anomaly_lines = "\n".join([
        f"- {a['product']}: {a['severity']} severity anomaly on {a['date']}"
        for a in ctx["recent_anomalies"]
    ]) or "No significant anomalies detected in the past 14 days."
    forecast_lines = "\n".join([
        f"- {f['product']}: {f['total_30d']} units forecast over next 30 days (~{f['avg_daily']} units/day)"
        for f in ctx["top_forecasts"]
    ]) or "No forecast data available."

    trend_direction = "up" if ctx["demand_trend_pct"] >= 0 else "down"
    trend_magnitude = abs(ctx["demand_trend_pct"])

    return f"""You are an inventory intelligence assistant writing a daily briefing for a non-technical business owner. Write a concise executive summary (4-6 short paragraphs) based on the data below.

Rules:
- Plain English only. No jargon. No bullet points. Flowing paragraphs.
- Be direct about what needs attention TODAY.
- End with a clear "What to do today" paragraph with 2-3 actions.
- Tone: confident, calm, like a trusted business advisor.
- Do NOT mention algorithms, model names, z-scores, or technical terms.

INVENTORY DATA ({ctx['generated_date']}):
Portfolio: {ctx['total_products']} products. Total stock value: ${ctx['total_stock_value']:,.2f}.

Stock Status:
{stockouts_text}
{critical_text}
{ctx['healthy_count']} products are at healthy stock levels.

Demand Trend: Overall demand this week is {trend_direction} {trend_magnitude}% vs last week.

Demand Forecast (next 30 days):
{forecast_lines}

Recent Alerts (last 14 days):
{anomaly_lines}

Now write the executive summary:"""


@router.get("/executive")
async def get_executive_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        context = await _gather_inventory_context(db)

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return {
                "summary": _fallback_summary(context),
                "context": context,
                "source": "fallback",
            }

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": _build_prompt(context)}],
        )

        return {
            "summary": message.content[0].text,
            "context": context,
            "source": "claude",
        }

    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


def _fallback_summary(ctx: dict) -> str:
    lines = [
        f"As of {ctx['generated_date']}, your inventory portfolio covers "
        f"{ctx['total_products']} products with a total stock value of "
        f"${ctx['total_stock_value']:,.2f}."
    ]
    if ctx["stockout_names"]:
        lines.append(
            f"Immediate attention required: {', '.join(ctx['stockout_names'])} "
            f"{'is' if len(ctx['stockout_names']) == 1 else 'are'} completely out of stock "
            f"and should be reordered today."
        )
    if ctx["critical_names"]:
        lines.append(
            f"The following products are running low: {', '.join(ctx['critical_names'])}. "
            f"Plan orders within the next few days."
        )
    trend = ctx["demand_trend_pct"]
    if abs(trend) >= 5:
        direction = "increased" if trend > 0 else "decreased"
        lines.append(f"Overall demand has {direction} by {abs(trend)}% compared to last week.")
    if ctx["recent_anomalies"]:
        flagged = list({a["product"] for a in ctx["recent_anomalies"]})
        lines.append(
            f"Unusual demand patterns detected for: {', '.join(flagged)}. "
            f"Review these products for supplier issues or unexpected demand shifts."
        )
    lines.append(
        "Action for today: "
        + (f"Reorder {ctx['stockout_names'][0]} immediately. " if ctx["stockout_names"] else "")
        + (f"Monitor {ctx['critical_names'][0]} stock levels. " if ctx["critical_names"] else "")
        + f"{ctx['healthy_count']} products are fully stocked — no action needed."
    )
    return " ".join(lines)