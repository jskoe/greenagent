"""Stub white agent server for local testing."""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn


app = FastAPI(title="Stub White Agent")


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


@app.post("/act", response_model=ActResponse)
async def act(request: ActRequest):
    """
    Stub white agent that returns deterministic actions.
    
    Simple strategy: look for clickable elements in DOM summary and click them.
    """
    observation = request.observation
    dom_summary = observation.get("dom_summary", [])
    step_idx = request.step_idx
    
    # Simple strategy: click first button/link if available
    if step_idx == 0:
        # First step: look for a button or link
        for element in dom_summary[:10]:  # Check first 10 elements
            tag = element.get("tag", "")
            if tag in ["button", "a"]:
                selector = element.get("selector", "")
                if selector:
                    return ActResponse(
                        action={
                            "type": "click",
                            "selector": selector,
                            "confidence": 0.8
                        },
                        thoughts=f"Clicking {tag} with selector {selector}",
                        info={"strategy": "first_clickable"}
                    )
    
    # If we have a specific instruction, try to match it
    instruction_lower = request.instruction.lower()
    if "price" in instruction_lower or "product" in instruction_lower:
        # Look for price-related elements
        for element in dom_summary:
            text = element.get("text", "").lower()
            selector = element.get("selector", "")
            if ("price" in text or "$" in text) and selector:
                return ActResponse(
                    action={
                        "type": "click",
                        "selector": selector,
                        "confidence": 0.9
                    },
                    thoughts=f"Found price element: {text}",
                    info={"strategy": "price_match"}
                )
    
    # Default: scroll down
    if step_idx < 3:
        return ActResponse(
            action={
                "type": "scroll",
                "delta_y": 500
            },
            thoughts="Scrolling to see more content",
            info={"strategy": "scroll"}
        )
    
    # After a few steps, stop
    return ActResponse(
        action={
            "type": "stop",
            "reason": "done"
        },
        thoughts="Task completed",
        info={"strategy": "stop"}
    )


@app.get("/health")
async def health():
    """Health check."""
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)

