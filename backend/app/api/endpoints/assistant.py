from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.services import ai_service  # 从core.services导入

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: list[str] = []

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    try:
        response = await ai_service.get_response(request.message, request.context)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 