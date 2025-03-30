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
    review_result: Annotated[ReviewResult, "Final review result"]

# Initialize the agent instances
@traceable(name="setup_extractors", run_type="chain")
def setup_extractors():
    """Set up extractors for the workflow"""
    experience_extractor = ExperienceExtractor()
    education_extractor = EducationExtractor()
    skills_extractor = SkillsExtractor()
    match_analyzer = MatchAnalyzer()
    score_generator = ScoreGenerator()
    
    return {
        "experience_extractor": experience_extractor,
        "education_extractor": education_extractor,
        "skills_extractor": skills_extractor,
        "match_analyzer": match_analyzer,
        "score_generator": score_generator
    }

# Define the workflow steps
@traceable(name="extract_experience", run_type="chain")
def extract_experience(state: ResumeReviewState) -> Dict[str, Any]:
    """Extract work experience from resume"""
    logger.info("Extracting work experience")
    agents = setup_extractors()
    experiences = agents["experience_extractor"].extract(state["resume"])
    
    return {"experiences": experiences}

@traceable(name="extract_education", run_type="chain")
def extract_education(state: ResumeReviewState) -> Dict[str, Any]:
    """Extract education from resume"""
    logger.info("Extracting education")
    agents = setup_extractors()
    education = agents["education_extractor"].extract(state["resume"])
    
    return {"education": education}

@traceable(name="extract_skills", run_type="chain")
def extract_skills(state: ResumeReviewState) -> Dict[str, Any]:
    """Extract skills from resume"""
    logger.info("Extracting skills")
    agents = setup_extractors()
    skills = agents["skills_extractor"].extract(
        state["resume"], 
        state["job_description"]
    )
    
    return {"skills": skills}

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

@traceable(name="generate_score", run_type="chain")
def generate_score(state: ResumeReviewState) -> Dict[str, Any]:
    """Generate overall score and recommendations"""
    logger.info("Generating score and recommendations")
    
    if not state.get("match_analysis"):
        logger.error("Match analysis not completed")
        return {}
    
    agents = setup_extractors()
    review_result = agents["score_generator"].generate(
        state["job_description"],
        state["match_analysis"]
    )
    
    return {"review_result": review_result}

def create_resume_review_graph():
    """Create the LangGraph workflow for resume review"""
    # Create a new graph
    graph = StateGraph(ResumeReviewState)
    
    # Add nodes to the graph for each step
    graph.add_node("extract_experience", extract_experience)
    graph.add_node("extract_education", extract_education)
    graph.add_node("extract_skills", extract_skills)
    graph.add_node("analyze_match", analyze_match)
    graph.add_node("generate_score", generate_score)
    
    # Set up the flow - run extractions in parallel
    graph.add_edge("extract_experience", "analyze_match")
    graph.add_edge("extract_education", "analyze_match")
    graph.add_edge("extract_skills", "analyze_match")
    
    # Then analyze and score
    graph.add_edge("analyze_match", "generate_score")
    graph.add_edge("generate_score", END)
    
    # Set the entry points - start with all three extraction processes simultaneously
    graph.set_entry_point("extract_experience")
    graph.set_entry_point("extract_education")
    graph.set_entry_point("extract_skills")
    
    # Compile the graph
    return graph.compile() 