from enum import Enum
from typing import List, Optional

class AIModel(str, Enum):
    GPT_4O = "gpt-4o"
    CLAUDE_SONNET = "claude-3.5-sonnet"
    OPENAI_O1 = "openai-o1"
    GEMINI_PRO = "gemini-1.5-pro"
    GROK_2 = "grok-2"

class AIRouterService:
    """
    Service responsible for analyzing user context and routing 
    to the optimal AI model provider.
    """

    @staticmethod
    def classify_intent(messages: List[dict]) -> AIModel:
        """
        Analyzes the last message to determine user intent.
        Prioritizes reasoning/code/math/search tasks.
        """
        if not messages:
            return AIModel.GPT_4O

        last_content = messages[-1].get("content", "").lower()
        
        # 1. Complex Reasoning & Coding
        if any(keyword in last_content for keyword in ["code", "debug", "python", "kotlin", "refactor", "error", "class"]):
            return AIModel.CLAUDE_SONNET
            
        # 2. Math & Logic Solving
        if any(keyword in last_content for keyword in ["math", "equation", "solve", "derivative", "integrate", "calculation"]):
            return AIModel.OPENAI_O1
            
        # 3. Research & Multimodal
        if any(keyword in last_content for keyword in ["search", "youtube", "summarize", "find", "latest", "news"]):
            return AIModel.GEMINI_PRO
            
        # 4. Real-time Social Context
        if any(keyword in last_content for keyword in ["twitter", "x", "trends", "current event", "breaking"]):
            return AIModel.GROK_2
            
        # 5. Default General Conversation
        return AIModel.GPT_4O