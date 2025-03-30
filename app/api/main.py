"""API endpoints for the AI Resume Reviewer"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
import json
from app.core.workflow import create_resume_review_graph
from app.utils.logger import setup_logging

# Set up logging
logger = setup_logging()

# Create app
app = FastAPI(
    title="AI Resume Reviewer",
    description="API for analyzing resumes against job descriptions",
    version="1.0.0"
)

# Define request models
class ReviewRequest(BaseModel):
    resume: str
    job_description: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "AI Resume Reviewer API is running"}

@app.post("/review")
async def review_resume(request: ReviewRequest):
    """Review a resume against a job description"""
    try:
        # Create the workflow graph
        graph = create_resume_review_graph()
        
        # Prepare input
        inputs = {
            "resume": request.resume,
            "job_description": request.job_description
        }
        
        # Execute the graph
        logger.info("Starting resume review workflow")
        result = graph.invoke(inputs)
        
        # Format response
        if "review_result" in result:
            review_result = result["review_result"]
            
            # Convert to JSON-serializable format
            response = {
                "overall_score": review_result.overall_score,
                "experience_match": review_result.match_details.experience_match,
                "education_match": review_result.match_details.education_match,
                "skills_match": review_result.match_details.skills_match,
                "strengths": review_result.match_details.strengths,
                "gaps": review_result.match_details.gaps,
                "recommendations": review_result.recommendations,
                "key_talking_points": review_result.key_talking_points
            }
            
            return response
        else:
            raise HTTPException(status_code=500, detail="Review processing failed")
    
    except Exception as e:
        logger.error(f"Error processing review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing review: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 