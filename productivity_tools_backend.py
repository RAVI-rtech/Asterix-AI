from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DocumentRequest(BaseModel):
    content: str

@router.post("/summarize")
async def summarize(request: DocumentRequest):
    # Call to LLM for summarization task
    return {"summary": "Summarized text output"}