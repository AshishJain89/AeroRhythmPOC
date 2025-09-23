from fastapi import APIRouter
from typing import Dict

router = APIRouter(prefix="/explanations", tags=["explanations"])

@router.get("/{explanation_id}")
async def get_explanation(explanation_id: int) -> Dict[str, str]:
    """Return dummy explanation text for a suggestion or action."""
    return {
        "explanationId": str(explanation_id),
        "explanation": "This suggestion is based on crew availability, compliance rules, and predicted efficiency."
    }
