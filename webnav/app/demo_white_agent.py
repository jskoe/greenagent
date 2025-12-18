"""Demo-ready white agent with verbose reasoning and step-by-step explanations."""
import os
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from .llm_white_agent import LLMWhiteAgent

# Configure logging for demo visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [WHITE AGENT] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Demo White Agent Server")

# Global agent instance
_demo_agent: Optional[LLMWhiteAgent] = None


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
    # Demo-specific fields
    input_summary: Optional[Dict[str, Any]] = None
    reasoning_steps: Optional[list] = None


def get_demo_agent() -> LLMWhiteAgent:
    """Get or create demo LLM agent instance."""
    global _demo_agent
    if _demo_agent is None:
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        model = os.getenv("LLM_MODEL")
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "500"))
        
        _demo_agent = LLMWhiteAgent(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.info(f"Initialized Demo White Agent: provider={provider}, model={_demo_agent.model}")
    
    return _demo_agent


def extract_input_summary(request: ActRequest) -> Dict[str, Any]:
    """Extract and summarize input for demo purposes."""
    obs = request.observation
    dom_summary = obs.get("dom_summary", [])
    
    return {
        "task_instruction": request.instruction,
        "current_step": request.step_idx,
        "page_url": obs.get("url", ""),
        "page_title": obs.get("title", ""),
        "available_elements_count": len(dom_summary),
        "sample_elements": dom_summary[:5] if dom_summary else [],
        "available_actions": request.action_space.get("allowed", [])
    }


def parse_reasoning_from_thoughts(thoughts: str) -> list:
    """Parse thoughts into structured reasoning steps for demo."""
    if not thoughts:
        return []
    
    # Try to extract reasoning steps from thoughts
    steps = []
    sentences = thoughts.split('. ')
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Identify reasoning step type
        if any(word in sentence.lower() for word in ["analyze", "examine", "look", "see"]):
            step_type = "observation"
        elif any(word in sentence.lower() for word in ["need", "should", "must", "require"]):
            step_type = "requirement"
        elif any(word in sentence.lower() for word in ["identify", "find", "select", "choose"]):
            step_type = "decision"
        elif any(word in sentence.lower() for word in ["click", "scroll", "type", "action"]):
            step_type = "action"
        else:
            step_type = "reasoning"
        
        steps.append({
            "step": i + 1,
            "type": step_type,
            "content": sentence
        })
    
    return steps


@app.post("/act", response_model=ActResponse)
async def act(request: ActRequest):
    """
    Demo white agent endpoint with verbose reasoning.
    
    Returns action with detailed input summary and reasoning steps for demonstration.
    """
    try:
        # Extract input summary for demo
        input_summary = extract_input_summary(request)
        
        # Log input for demo visibility
        logger.info("=" * 60)
        logger.info(f"STEP {request.step_idx} - INPUT RECEIVED")
        logger.info("=" * 60)
        logger.info(f"Task Instruction: {request.instruction}")
        logger.info(f"Current URL: {request.observation.get('url', '')}")
        logger.info(f"Page Title: {request.observation.get('title', '')}")
        logger.info(f"Available Elements: {len(request.observation.get('dom_summary', []))}")
        logger.info(f"Available Actions: {request.action_space.get('allowed', [])}")
        
        # Get agent and decide action
        agent = get_demo_agent()
        result = await agent.decide_action(
            instruction=request.instruction,
            step_idx=request.step_idx,
            observation=request.observation,
            action_space=request.action_space,
            run_id=request.run_id,
            task_id=request.task_id
        )
        
        # Parse reasoning steps
        reasoning_steps = parse_reasoning_from_thoughts(result.get("thoughts", ""))
        
        # Log output for demo visibility
        logger.info("=" * 60)
        logger.info(f"STEP {request.step_idx} - OUTPUT GENERATED")
        logger.info("=" * 60)
        logger.info(f"Action Type: {result['action'].get('type', 'unknown')}")
        logger.info(f"Action Details: {json.dumps(result['action'], indent=2)}")
        logger.info(f"Reasoning: {result.get('thoughts', 'No reasoning provided')}")
        logger.info("=" * 60)
        
        return ActResponse(
            action=result["action"],
            thoughts=result.get("thoughts"),
            info=result.get("info"),
            input_summary=input_summary,
            reasoning_steps=reasoning_steps
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
        agent = get_demo_agent()
        return {
            "ok": True,
            "provider": agent.provider,
            "model": agent.model,
            "mode": "demo"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with demo information."""
    return {
        "name": "Demo White Agent Server",
        "version": "1.0.0",
        "description": "White agent with verbose reasoning for demonstrations",
        "endpoints": {
            "act": "POST /act - Get next action with detailed reasoning",
            "health": "GET /health - Health check"
        },
        "features": [
            "Verbose logging of inputs and outputs",
            "Structured reasoning steps",
            "Input summary for each step",
            "Demo-ready explanations"
        ],
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
    
    logger.info("=" * 60)
    logger.info("STARTING DEMO WHITE AGENT SERVER")
    logger.info("=" * 60)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Provider: {os.getenv('LLM_PROVIDER', 'openai')}")
    logger.info(f"Model: {os.getenv('LLM_MODEL', 'default')}")
    logger.info("=" * 60)
    logger.info("Ready for demo! All actions will be logged with reasoning.")
    logger.info("=" * 60)
    
    uvicorn.run(app, host=host, port=port)

