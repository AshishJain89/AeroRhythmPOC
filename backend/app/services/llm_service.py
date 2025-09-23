import openai
from ..core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

async def process_query(user_id: int, query: str, context: str = "None", db: AsyncSession = None) -> dict:
    openai.api_key = settings.OPENAI_API_KEY
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"User context: {context}"},
                {"role": "user", "content": query}
            ]
        )
        reply = response.choices[0].message.content
        return {"reply": reply, "actions": [], "explanation_id": None}
    except Exception as e:
        return {"reply": f"Error: {str(e)}", "actions": [], "explanation_id": None}