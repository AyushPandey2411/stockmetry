"""app/api/v1/ai_chat.py — Claude AI assistant with inventory context."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...core.config import settings
from ...models.user import User
from ...ml.optimizer import run_optimization
from ...models.anomaly import AnomalyRecord
from ...models.product import Product

router = APIRouter(prefix="/chat", tags=["AI Assistant"])


class ChatMessage(BaseModel):
    role: str    # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    api_key: str = ""


def _build_context(db: Session) -> str:
    recs  = run_optimization(db)
    prods = db.query(Product).filter(Product.is_active==True).all()
    anoms = db.query(AnomalyRecord).filter(AnomalyRecord.severity=="high").limit(10).all()

    lines = ["=== STOCKMETRY INVENTORY CONTEXT ===\n"]
    lines.append("PRODUCT STATUS:")
    for r in recs:
        lines.append(f"  {r['name']} ({r['sku']}): stock={r['current_stock']} | "
                     f"status={r['status']} | EOQ={r['eoq']} | "
                     f"days_left={r['days_of_stock']} | saving={r['pct_saving']}%")
    lines.append(f"\nANNUAL SAVINGS OPPORTUNITY: ${sum(r['annual_saving'] for r in recs):,.0f}")
    lines.append(f"\nHIGH-SEVERITY ANOMALIES (last 10):")
    prod_names = {p.id: p.name for p in prods}
    for a in anoms:
        lines.append(f"  {prod_names.get(a.product_id,'?')} on {a.date}: "
                     f"demand={a.demand} (avg={a.avg_demand}) z={a.z_score} [{a.anomaly_type}]")
    return "\n".join(lines)


SYSTEM_PROMPT = """You are Stockmetry's AI inventory analyst — precise, data-driven, and concise.
You have real-time access to the user's inventory data shown below.
Always ground answers in the data. Quantify in dollars when possible. Be actionable.

{context}"""

DEMO_RESPONSES = {
    "stockout": "Based on your data, the most urgent risks are products in **STOCKOUT** or **REORDER** status. Check the Optimization page for exact EOQ quantities and reorder points.",
    "forecast": "Your XGBoost model achieves ~19% MAPE — 23% better than a naive baseline. The Forecasting page shows 30-day demand projections with 95% confidence intervals per product.",
    "saving":   "EOQ optimization identifies approximately **$26,000+ in annual savings** by matching order quantities to the mathematical cost minimum rather than arbitrary 30-day cycles.",
    "anomaly":  "Isolation Forest detected anomalies across your product portfolio. High-severity events (|z| > 3.5) are shown first in the Anomaly Detection page.",
}

def _demo_response(q: str) -> str:
    q = q.lower()
    for k, v in DEMO_RESPONSES.items():
        if k in q: return v
    return ("I can analyze **stockout risks**, **demand forecasts**, **EOQ savings**, and **anomaly patterns** "
            "from your live inventory data. Add your Anthropic API key in settings for full Claude AI responses.")


@router.post("/")
async def chat(req: ChatRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    key = req.api_key or settings.ANTHROPIC_API_KEY
    if not key:
        return {"response": _demo_response(req.messages[-1].content if req.messages else "")}
    try:
        import anthropic
        context = _build_context(db)
        client  = anthropic.Anthropic(api_key=key)
        msgs    = [{"role": m.role, "content": m.content} for m in req.messages[-10:]]
        res     = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=800,
            system=SYSTEM_PROMPT.format(context=context), messages=msgs,
        )
        return {"response": res.content[0].text}
    except Exception as e:
        raise HTTPException(500, str(e))
