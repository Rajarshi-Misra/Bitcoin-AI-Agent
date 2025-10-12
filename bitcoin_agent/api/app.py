"""
FastAPI application entry point for Bitcoin AI Agent
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bitcoin_agent.agent import process_user_input
from bitcoin_agent.crypto import get_crypto_price


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application
    """
    app = FastAPI(
        title="Bitcoin AI Agent API",
        description="Production-ready Bitcoin AI Assistant with RAG and multi-user support",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


# Create the FastAPI application instance
app = create_app()


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message to the AI agent", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI agent response")
    session_id: Optional[str] = Field(None, description="Session ID for this conversation")


class PriceResponse(BaseModel):
    """Price response model"""
    price_inr: float = Field(..., description="Bitcoin price in INR")
    currency: str = Field(default="INR", description="Currency code")
    crypto: str = Field(default="bitcoin", description="Cryptocurrency name")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    message: str


# API Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bitcoin AI Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/chat",
            "price": "/price"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        message="Bitcoin AI Agent is running"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for conversing with the Bitcoin AI agent
    
    Args:
        request: ChatRequest with user message and optional session_id
        
    Returns:
        ChatResponse with AI agent response
    """
    try:
        response = process_user_input(request.message)
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/price", response_model=PriceResponse)
async def get_price(crypto: str = "bitcoin", currency: str = "INR"):
    """
    Get current cryptocurrency price
    
    Args:
        crypto: Cryptocurrency name (default: bitcoin)
        currency: Currency code (default: INR)
        
    Returns:
        PriceResponse with current price
    """
    try:
        price = get_crypto_price(crypto=crypto, currency=currency)
        
        if isinstance(price, str) and price.startswith("Error"):
            raise HTTPException(status_code=500, detail=price)
            
        return PriceResponse(
            price_inr=float(price),
            currency=currency,
            crypto=crypto
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid price value: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price: {str(e)}")


def main():
    """
    Main entry point for running the application
    Can be called via: python -m bitcoin_agent.api.app
    Or via the script entry point: bitcoin-agent
    """
    uvicorn.run(
        "bitcoin_agent.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    main()

