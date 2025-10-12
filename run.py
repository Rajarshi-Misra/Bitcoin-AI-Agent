#!/usr/bin/env python3
"""
Simple entry point script to run the Bitcoin AI Agent API server

Usage:
    python run.py
    
Or use uvicorn directly:
    uvicorn bitcoin_agent.api.app:app --reload
"""

if __name__ == "__main__":
    from bitcoin_agent.api.app import main
    main()

