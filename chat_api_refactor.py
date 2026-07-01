import asyncio
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from backend.app.services.router import AIRouterService

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    language: str = "en" 

router = APIRouter()

def select_best_model(messages: List[Message]) -> str:
    """
    AI Router: Dynamically selects the best model based on the user's prompt context.
    The user NEVER selects models manually.
    """
    if not messages:
        return "gpt-4o"
        
    last_message = messages[-1].content.lower()
    
    # Logic matching your premium features
    if any(keyword in last_message for keyword in ["code", "debug", "python", "kotlin", "error"]):
        return "claude-3.5-sonnet" # Best for complex coding and long reasoning
    elif any(keyword in last_message for keyword in ["math", "equation", "solve", "calculate"]):
        return "openai-o1" # Best for complex math solving
    elif any(keyword in last_message for keyword in ["latest", "news", "search", "youtube", "summarize"]):
        return "gemini-1.5-pro" # Best for multimodal, YouTube, and web search tasks
    elif any(keyword in last_message for keyword in ["twitter", "x", "real-time"]):
        return "grok-2" # Best for real-time social context
    else:
        return "gpt-4o" # Default for general, conversational, ChatGPT-like tasks

async def generate_chat_stream(model: str, messages: List[Message], language: str):
    """
    Connects to the respective AI provider (OpenAI/Anthropic/Google/etc.) SDK.
    Streams the response back to the Android client chunk-by-chunk.
    """
    yield f"data: {json.dumps({'model_used': model, 'status': 'routing'})}\n\n"
    await asyncio.sleep(0.1)

    # In production, this would be an async generator from the actual AI SDK.
    response_text = f"This response was routed to {model} based on your intent. AstraMind understands your request."
    if language == "te":
        response_text = f"ఈ ప్రతిస్పందన మీ ఉద్దేశ్యం ఆధారంగా {model}కి పంపబడింది. ఆస్ట్రామైండ్ మీ అభ్యర్థనను అర్థం చేసుకుంటుంది."
    if language == "te":
        response_text = f"ఇది {model} ద్వారా ప్రాసెస్ చేయబడిన నిజ-సమయ ప్రతిస్పందన. ఆస్ట్రామైండ్ మీ అభ్యర్థనను ఖచ్చితంగా అర్థం చేసుకుంటుంది."

    words = response_text.split(" ")
    for word in words:
        chunk = {"content": word + " "}
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.05) # Simulate AI token generation delay

    yield "data: [DONE]\n\n"

@router.post("/stream")
async def chat_endpoint(request: ChatRequest):
    try:
        messages_dict = [m.dict() for m in request.messages]
        best_model = AIRouterService.classify_intent(messages_dict)
        
        return StreamingResponse(
            generate_chat_stream(best_model, request.messages, request.language),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))