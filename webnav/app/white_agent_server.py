"""Standalone white agent server with LLM support."""
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from .llm_white_agent import LLMWhiteAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM White Agent Server")


class ActRequest(BaseModel):
    run_id: str
    task_id: str
    instruction: str
    step_idx: int
    observation: Dict[str, Any]
    action_space: Dict[str, Any]


class ActResponse(BaseModel):
    action: Dict[str, Any]
    thoughts: Optional[str] = None
    info: Optional[Dict[str, Any]] = None


# Initialize LLM agent (lazy loading)
_llm_agent: Optional[LLMWhiteAgent] = None


def get_llm_agent() -> LLMWhiteAgent:
    """Get or create LLM agent instance."""
    global _llm_agent
    if _llm_agent is None:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        model = os.getenv("LLM_MODEL")  # None = use default
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "500"))
        
        _llm_agent = LLMWhiteAgent(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.info(f"Initialized LLM agent: provider={provider}, model={_llm_agent.model}")
    
    return _llm_agent


@app.post("/act", response_model=ActResponse)
async def act(request: ActRequest):
    """
    LLM-powered white agent that makes intelligent navigation decisions.
    
    Configure via environment variables:
    - LLM_PROVIDER: "openai" or "anthropic" (default: "openai")
    - LLM_MODEL: Model name (defaults to gpt-4o-mini for OpenAI, claude-3-5-haiku for Anthropic)
    - OPENAI_API_KEY: OpenAI API key (required if provider=openai)
    - ANTHROPIC_API_KEY: Anthropic API key (required if provider=anthropic)
    - LLM_TEMPERATURE: Sampling temperature 0.0-1.0 (default: 0.1)
    - LLM_MAX_TOKENS: Max tokens for response (default: 500)
    """
    try:
        agent = get_llm_agent()
        
        # Call LLM to decide action
        result = await agent.decide_action(
            instruction=request.instruction,
            step_idx=request.step_idx,
            observation=request.observation,
            action_space=request.action_space,
            run_id=request.run_id,
            task_id=request.task_id
        )
        
        return ActResponse(
            action=result["action"],
            thoughts=result.get("thoughts"),
            info=result.get("info")
        )
        
    except Exception as e:
        logger.error(f"Error in /act endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error deciding action: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        agent = get_llm_agent()
        return {
            "ok": True,
            "provider": agent.provider,
            "model": agent.model
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with info."""
    return {
        "name": "LLM White Agent Server",
        "version": "1.0.0",
        "endpoints": {
            "act": "POST /act - Get next action",
            "health": "GET /health - Health check"
        },
        "configuration": {
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "model": os.getenv("LLM_MODEL", "default"),
            "temperature": os.getenv("LLM_TEMPERATURE", "0.1"),
            "max_tokens": os.getenv("LLM_MAX_TOKENS", "500")
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("WHITE_AGENT_PORT", "9000"))
    host = os.getenv("WHITE_AGENT_HOST", "0.0.0.0")
    
    logger.info(f"Starting LLM White Agent Server on {host}:{port}")
    logger.info(f"Provider: {os.getenv('LLM_PROVIDER', 'openai')}")
    logger.info(f"Model: {os.getenv('LLM_MODEL', 'default')}")
    
    uvicorn.run(app, host=host, port=port)

