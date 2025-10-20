from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
from pathlib import Path

from .models import TaskRequest, Report, HealthResponse, ResetResponse
from .controller import get_controller, cleanup_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    # Startup
    print("Starting WebNav Green Agent...")
    await get_controller()
    print("WebNav Green Agent started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down WebNav Green Agent...")
    await cleanup_controller()
    print("WebNav Green Agent shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="WebNav Green Agent",
    description="A green agent evaluation host for Mind2Web tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files - use absolute path to sites directory
sites_dir = Path(__file__).parent.parent / "sites"
app.mount("/site", StaticFiles(directory=str(sites_dir)), name="static")


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": "WebNav Green Agent",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "reset": "/reset",
            "task": "/task",
            "static": "/site/product.html"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(ok=True)


@app.post("/reset", response_model=ResetResponse)
async def reset():
    """Reset the controller and clean up resources."""
    try:
        controller = await get_controller()
        await controller.reset()
        await get_controller()  # Reinitialize
        return ResetResponse(reset=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/task", response_model=Report)
async def execute_task(task_request: TaskRequest):
    """Execute a task and return the report."""
    try:
        controller = await get_controller()
        report = await controller.execute_task(task_request)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
