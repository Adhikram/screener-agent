"""LangGraph workflow for the AI Resume Reviewer"""
from typing import Dict, Any, List, TypedDict, Annotated
import os
from langgraph.graph import StateGraph, END
from langsmith import traceable
from app.agents.extractors import ExperienceExtractor, EducationExtractor, SkillsExtractor
from app.agents.extractors import Experience, Education, Skill
from app.agents.analyzers import MatchAnalyzer, ScoreGenerator, MatchAnalysis, ReviewResult
from app.utils.logger import setup_logging

# Set up logger
logger = setup_logging()

# Define the state structure
class ResumeReviewState(TypedDict):
    resume: str
    job_description: str
    experiences: Annotated[List[Experience], "Extracted work experiences"]
    education: Annotated[List[Education], "Extracted education"]
    skills: Annotated[List[Skill], "Extracted skills"]
    match_analysis: Annotated[MatchAnalysis, "Analysis of match between resume and job"]

# Initialize the agent instances
@traceable(name="setup_extractors", run_type="chain")
def setup_extractors():
    """Set up extractors for the workflow"""
    experience_extractor = ExperienceExtractor()
    education_extractor = EducationExtractor()
    skills_extractor = SkillsExtractor()
    match_analyzer = MatchAnalyzer()
    
    return {
        "experience_extractor": experience_extractor,
        "education_extractor": education_extractor,
        "skills_extractor": skills_extractor,
        "match_analyzer": match_analyzer
    }

# Define the combined extraction function
@traceable(name="extract", run_type="chain")
def extract(state: ResumeReviewState) -> Dict[str, Any]:
    """Extract all information from resume: experience, education, and skills"""
    logger.info("Extracting all resume information")
    agents = setup_extractors()
    
    # Extract all information
    experiences = agents["experience_extractor"].extract(state["resume"])
    education = agents["education_extractor"].extract(state["resume"])
    skills = agents["skills_extractor"].extract(
        state["resume"], 
        state["job_description"]
    )
    
    return {
        "experiences": experiences,
        "education": education,
        "skills": skills
    }

@traceable(name="analyze_match", run_type="chain")
def analyze_match(state: ResumeReviewState) -> Dict[str, Any]:
    """Analyze match between resume and job description"""
    logger.info("Analyzing match")
    
    # Wait for all extractions to complete
    if not state.get("experiences") or not state.get("education") or not state.get("skills"):
        logger.error("Extraction steps not completed")
        return {}
    
    agents = setup_extractors()
    match_analysis = agents["match_analyzer"].analyze(
        state["job_description"],
        state["experiences"],
        state["education"],
        state["skills"]
    )
    
    return {"match_analysis": match_analysis}

def create_resume_review_graph():
    """Create the LangGraph workflow for resume review"""
    # Create a new graph
    graph = StateGraph(ResumeReviewState)
    
    # Add nodes to the graph for each step
    graph.add_node("extract", extract)
    graph.add_node("analyze_match", analyze_match)
    
    # Set up the flow - extraction followed by analysis
    graph.add_edge("extract", "analyze_match")
    graph.add_edge("analyze_match", END)
    
    # Set the entry point - start with extraction
    graph.set_entry_point("extract")
    
    # Compile the graph
    return graph.compile() 