from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

async def process_query(user_id: int, query: str, context: str = "None", db: AsyncSession = None) -> Dict:
    # Dummy async implementation
    if "how many uncovered flights" in query.lower():
        return {
            "reply": "Currently, there are 15 uncovered flights in the selected period.",
            "actions": [],
            "explanationId": None
        }
    return {
        "reply": "I'm not sure about that. Please refer to the documentation or try again.",
        "actions": [],
        "explanationId": None
    }
