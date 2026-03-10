"""
app/api/v1/executive_summary.py

GET /api/v1/summary/executive
Returns a plain-English AI-generated summary of the current inventory state.
Designed for non-technical business users (owners, ops managers, executives).
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
from app.models.forecast import Forecast
from app.models.anomaly import Anomaly

router = APIRouter()


async def _gather_inventory_context(db: AsyncSession) -> dict:
    """Pull all the data Claude needs to write the summary."""

    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    # ── Products ────────────────────────────────────────────────
    products_result = await db.execute(select(Product))
    products = products_result.scalars().all()

    stockout_products   = [p for p in products if p.current_stock == 0]
    critical_products   = [p for p in products if 0 < p.current_stock <= (p.reorder_point or 0)]
    healthy_products    = [p for p in products if p.current_stock > (p.reorder_point or 0)]

    total_stock_value = sum(
        (p.current_stock or 0) * (p.unit_cost or 0) for p in products
    )

    # ── Recent anomalies (last 14 days) ────────────────────────
    anomaly_result = await db.execute(
        select(Anomaly, Product.name)
        .join(Product, Anomaly.product_id == Product.id)
        .where(Anomaly.date >= today - timedelta(days=14))
        .where(Anomaly.severity.in_(["HIGH", "MEDIUM"]))
        .order_by(desc(Anomaly.date))
        .limit(5)
    )
    recent_anomalies = anomaly_result.all()

    # ── Forecasts (next 30 days, highest demand products) ──────
    forecast_result = await db.execute(
        select(
            Forecast.product_id,
            Product.name,
            func.sum(Forecast.predicted_quantity).label("total_forecast"),
            func.avg(Forecast.predicted_quantity).label("avg_daily")
        )
        .join(Product, Forecast.product_id == Product.id)
        .where(Forecast.forecast_date >= today)
        .where(Forecast.forecast_date <= today + timedelta(days=30))
        .group_by(Forecast.product_id, Product.name)
        .order_by(desc("total_forecast"))
        .limit(5)
    )
    top_forecasts = forecast_result.all()

    # ── Recent demand trend (last 7 vs previous 7 days) ────────
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
    prev_7_total   = prev_7.scalar() or 1  # avoid div by zero

    demand_trend_pct = round(((recent_7_total - prev_7_total) / prev_7_total) * 100, 1)

    return {
        "total_products":      len(products),
        "stockout_count":      len(stockout_products),
        "critical_count":      len(critical_products),
        "healthy_count":       len(healthy_products),
        "total_stock_value":   round(total_stock_value, 2),
        "stockout_names":      [p.name for p in stockout_products],
        "critical_names":      [p.name for p in critical_products],
        "demand_trend_pct":    demand_trend_pct,
        "recent_anomalies":    [
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
                "product":     row.name,
                "total_30d":   round(row.total_forecast or 0),
                "avg_daily":   round(row.avg_daily or 0, 1)
            }
            for row in top_forecasts
        ],
        "generated_date": str(today),
    }


def _build_prompt(ctx: dict) -> str:
    """Build the prompt that tells Claude what to write."""

    stockouts_text = (
        f"The following products are completely out of stock: {', '.join(ctx['stockout_names'])}."
        if ctx["stockout_names"]
        else "No products are currently out of stock."
    )

    critical_text = (
        f"These products are running critically low and approaching their reorder points: {', '.join(ctx['critical_names'])}."
        if ctx["critical_names"]
        else "No products are in a critical low-stock state."
    )

    anomaly_lines = "\n".join([
        f"- {a['product']}: {a['severity']} severity anomaly on {a['date']} (z-score: {a['z_score']})"
        for a in ctx["recent_anomalies"]
    ]) or "No significant anomalies detected in the past 14 days."

    forecast_lines = "\n".join([
        f"- {f['product']}: {f['total_30d']} units forecast over next 30 days (~{f['avg_daily']} units/day)"
        for f in ctx["top_forecasts"]
    ]) or "No forecast data available."

    trend_direction = "up" if ctx["demand_trend_pct"] >= 0 else "down"
    trend_magnitude = abs(ctx["demand_trend_pct"])

    return f"""You are an inventory intelligence assistant writing a daily briefing for a non-technical business owner or operations manager. They do not know what XGBoost or z-scores are. They understand plain business language: money, stock, risk, and action.

Write a concise executive summary (4–6 short paragraphs) based on the inventory data below. 

Rules:
- Write in plain English. No jargon. No bullet points. Flowing paragraphs only.
- Be direct about what needs attention TODAY.
- Mention dollar values and product names where relevant.
- End with a clear "What to do today" paragraph with 2–3 prioritised actions.
- Tone: confident, calm, like a trusted business advisor.
- Do NOT mention algorithms, model names, z-scores, MAPE, EOQ, or any technical terms.

INVENTORY DATA ({ctx['generated_date']}):

Portfolio: {ctx['total_products']} products tracked. Total stock value: ${ctx['total_stock_value']:,.2f}.

Stock Status:
{stockouts_text}
{critical_text}
{ctx['healthy_count']} products are at healthy stock levels.

Demand Trend:
Overall demand this week is {trend_direction} {trend_magnitude}% compared to last week.

Demand Forecast (next 30 days — top products):
{forecast_lines}

Recent Alerts (last 14 days):
{anomaly_lines}

Now write the executive summary:"""


@router.get("/executive")
async def get_executive_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate a plain-English AI summary of current inventory state.
    Uses Claude Sonnet to write a briefing suitable for non-technical executives.
    """
    try:
        # Gather live data from the database
        context = await _gather_inventory_context(db)

        # Call Claude
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            # Return a graceful fallback if no API key is configured
            return {
                "summary": _fallback_summary(context),
                "context": context,
                "source": "fallback",
            }

        client = anthropic.Anthropic(api_key=api_key)
        prompt = _build_prompt(context)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )

        summary_text = message.content[0].text

        return {
            "summary": summary_text,
            "context": context,
            "source": "claude",
        }

    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


def _fallback_summary(ctx: dict) -> str:
    """
    Rule-based summary when no API key is available.
    Still useful — better than nothing.
    """
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
            f"The following products are running low and approaching reorder levels: "
            f"{', '.join(ctx['critical_names'])}. Plan orders within the next few days."
        )

    trend = ctx["demand_trend_pct"]
    if abs(trend) >= 5:
        direction = "increased" if trend > 0 else "decreased"
        lines.append(
            f"Overall demand has {direction} by {abs(trend)}% compared to last week."
        )

    if ctx["recent_anomalies"]:
        products_flagged = list({a["product"] for a in ctx["recent_anomalies"]})
        lines.append(
            f"Unusual demand patterns were detected for: {', '.join(products_flagged)}. "
            f"Review these products for supplier issues or unexpected demand shifts."
        )

    lines.append(
        f"Action for today: "
        + (f"Reorder {ctx['stockout_names'][0]} immediately. " if ctx["stockout_names"] else "")
        + (f"Monitor {ctx['critical_names'][0]} stock levels. " if ctx["critical_names"] else "")
        + f"{ctx['healthy_count']} products are fully stocked — no action needed."
    )

    return " ".join(lines)