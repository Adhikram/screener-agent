"""Analyzer agents for the AI Resume Reviewer"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from app.core.models import get_openai_model, create_prompt
from app.agents.extractors import Experience, Education, Skill

class MatchAnalysis(BaseModel):
    experience_match: float = Field(description="How well the experience matches the job requirements (0-1)")
    education_match: float = Field(description="How well the education matches the job requirements (0-1)")
    skills_match: float = Field(description="How well the skills match the job requirements (0-1)")
    strengths: List[str] = Field(description="Candidate's key strengths for this role")
    gaps: List[str] = Field(description="Identified gaps in candidate's profile")

class ReviewResult(BaseModel):
    overall_score: float = Field(description="Overall match score (0-1)")
    match_details: MatchAnalysis = Field(description="Detailed match analysis")
    recommendations: List[str] = Field(description="Recommendations for improving the resume")
    key_talking_points: List[str] = Field(description="Key talking points for an interview")

class MatchAnalyzer:
    """Agent to analyze the match between resume and job description"""
    
    def __init__(self):
        self.model = get_openai_model()
        self.parser = PydanticOutputParser(pydantic_object=MatchAnalysis)
        
        self.prompt = create_prompt("""
        You are an AI assistant that analyzes how well a candidate's profile matches a job description.
        
        Job Description:
        {job_description}
        
        Candidate's Experience:
        {experiences}
        
        Candidate's Education:
        {education}
        
        Candidate's Skills:
        {skills}
        
        Analyze the match between the candidate's profile and the job requirements.
        Provide:
        - Experience match score (0-1)
        - Education match score (0-1)
        - Skills match score (0-1)
        - Key strengths relevant to this role
        - Gaps in the candidate's profile compared to requirements
        
        {format_instructions}
        """)
        
    def analyze(self, 
                job_description: str, 
                experiences: List[Experience], 
                education: List[Education], 
                skills: List[Skill]) -> MatchAnalysis:
        """Analyze match between resume and job description"""
        response = self.model.invoke(
            self.prompt.format(
                job_description=job_description,
                experiences=experiences,
                education=education,
                skills=skills,
                format_instructions=self.parser.get_format_instructions()
            )
        )
        
        try:
            return self.parser.parse(response.content)
        except Exception as e:
            print(f"Error parsing match analysis: {e}")
            return MatchAnalysis(
                experience_match=0.0,
                education_match=0.0,
                skills_match=0.0,
                strengths=[],
                gaps=["Error analyzing resume"]
            )

class ScoreGenerator:
    """Agent to generate overall score and recommendations"""
    
    def __init__(self):
        self.model = get_openai_model()
        self.parser = PydanticOutputParser(pydantic_object=ReviewResult)
        
        self.prompt = create_prompt("""
        You are an AI assistant that generates an overall score and recommendations for a job applicant.
        
        Job Description:
        {job_description}
        
        Match Analysis:
        {match_analysis}
        
        Generate:
        - An overall match score (0-1)
        - Specific recommendations to improve the resume for this job
        - Key talking points for an interview
        
        {format_instructions}
        """)
        
    def generate(self, job_description: str, match_analysis: MatchAnalysis) -> ReviewResult:
        """Generate overall score and recommendations"""
        response = self.model.invoke(
            self.prompt.format(
                job_description=job_description,
                match_analysis=match_analysis,
                format_instructions=self.parser.get_format_instructions()
            )
        )
        
        try:
            return self.parser.parse(response.content)
        except Exception as e:
            print(f"Error parsing review result: {e}")
            return ReviewResult(
                overall_score=0.0,
                match_details=match_analysis,
                recommendations=["Error generating recommendations"],
                key_talking_points=[]
            ) 