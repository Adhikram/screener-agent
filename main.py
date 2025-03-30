#!/usr/bin/env python
"""
AI Resume Reviewer using LangGraph, Swarm Agents, and LangSmith
"""
import os
import json
from dotenv import load_dotenv
from app.core.workflow import create_resume_review_graph
from app.utils.logger import setup_logging
from app.agents.extractors import Experience, Education, Skill
from app.agents.analyzers import MatchAnalysis, ReviewResult

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Custom JSON Encoder to handle our custom classes
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Experience, Education, Skill, MatchAnalysis, ReviewResult)):
            return obj.__dict__
        return super().default(obj)

def main():
    """Main entry point for the AI Resume Reviewer"""
    logger.info("Starting AI Resume Reviewer")
    
    # Create the LangGraph workflow
    graph = create_resume_review_graph()
    
    # Example input from resume.txt and jd.txt
    with open("resume.txt", "r") as f:
        resume = f.read()
    with open("jd.txt", "r") as f:
        job_description = f.read()
    inputs = {
        "resume": resume,
        "job_description": job_description
    }
    
    # Execute the graph
    result = graph.invoke(inputs)
    
    # Print the result
    print(f"Resume Review Result: {result}")
    with open("result.json", "w") as f:
        json.dump(result, f, cls=CustomEncoder, indent=2)

if __name__ == "__main__":
    main() 