#!/usr/bin/env python
"""Run the AI Resume Reviewer API server"""
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Start the API server"""
    print("Starting AI Resume Reviewer API...")
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Run server
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main() 