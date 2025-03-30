"""Extractor agents for the AI Resume Reviewer"""
from typing import Dict, Any, List
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, create_model
from app.core.models import get_openai_model, create_prompt
import json
import re

# Define Pydantic models for structured output
class Experience(BaseModel):
    company: str = Field(description="Name of the company")
    title: str = Field(description="Job title")
    start_date: str = Field(description="Start date of the job")
    end_date: str = Field(description="End date of the job, or 'Present' if current")
    description: str = Field(description="Description of responsibilities and achievements")
    skills_used: List[str] = Field(description="Skills demonstrated in this role")

class Education(BaseModel):
    institution: str = Field(description="Name of the educational institution")
    degree: str = Field(description="Degree earned")
    field_of_study: str = Field(description="Field or major of study")
    graduation_date: str = Field(description="Date of graduation")
    achievements: List[str] = Field(description="Notable achievements during education")

class Skill(BaseModel):
    name: str = Field(description="Name of the skill")
    category: str = Field(description="Category (technical, soft, domain)")
    level: str = Field(description="Proficiency level (beginner, intermediate, expert)")
    relevance: float = Field(description="Relevance to the job (0-1)")

# Create list models
ExperienceList = create_model('ExperienceList', items=(List[Experience], ...))
EducationList = create_model('EducationList', items=(List[Education], ...))
SkillList = create_model('SkillList', items=(List[Skill], ...))

class ExperienceExtractor:
    """Agent to extract work experience from a resume"""
    
    def __init__(self):
        self.model = get_openai_model()
        self.single_parser = PydanticOutputParser(pydantic_object=Experience)
        self.list_parser = PydanticOutputParser(pydantic_object=ExperienceList)
        
        self.prompt = create_prompt("""
        You are an AI assistant that extracts work experience information from resumes.
        
        Resume:
        {resume}
        
        Extract all work experiences from this resume. Return a list of experiences, for each position, provide:
        - Company name
        - Job title
        - Start and end dates
        - Description of responsibilities and achievements
        - Skills demonstrated
        
        Format your response as a JSON list of objects where each object represents one work experience.
        
        Example format:
        [
            {{
                "company": "Company Name",
                "title": "Job Title",
                "start_date": "Start Date",
                "end_date": "End Date",
                "description": "Description of responsibilities",
                "skills_used": ["Skill 1", "Skill 2"]
            }},
            ...
        ]
        """)
        
    def extract(self, resume: str) -> List[Experience]:
        """Extract work experience from resume"""
        response = self.model.invoke(
            self.prompt.format(
                resume=resume
            )
        )
        
        experiences = []
        try:
            # Extract JSON from the response
            text_content = response.content
            # Find JSON array using regex
            matches = re.search(r'(\[.*\])', text_content, re.DOTALL)
            if matches:
                json_str = matches.group(1)
                # Parse the JSON
                experience_list = json.loads(json_str)
                
                # Parse each experience
                for exp_data in experience_list:
                    try:
                        exp = Experience(**exp_data)
                        experiences.append(exp)
                    except Exception as e:
                        print(f"Error parsing single experience: {e}")
            else:
                # Try to parse as a single object
                try:
                    exp = self.single_parser.parse(text_content)
                    experiences.append(exp)
                except Exception as e:
                    print(f"Error parsing as single experience: {e}")
        except Exception as e:
            print(f"Error parsing experiences: {e}")
            
        return experiences

class EducationExtractor:
    """Agent to extract education information from a resume"""
    
    def __init__(self):
        self.model = get_openai_model()
        self.single_parser = PydanticOutputParser(pydantic_object=Education)
        self.list_parser = PydanticOutputParser(pydantic_object=EducationList)
        
        self.prompt = create_prompt("""
        You are an AI assistant that extracts education information from resumes.
        
        Resume:
        {resume}
        
        Extract all education experiences from this resume. Return a list of education entries, for each, provide:
        - Institution name
        - Degree earned
        - Field of study
        - Graduation date
        - Notable achievements
        
        Format your response as a JSON list of objects where each object represents one education entry.
        
        Example format:
        [
            {{
                "institution": "University Name",
                "degree": "Degree Earned",
                "field_of_study": "Field of Study",
                "graduation_date": "Graduation Date",
                "achievements": ["Achievement 1", "Achievement 2"]
            }},
            ...
        ]
        """)
        
    def extract(self, resume: str) -> List[Education]:
        """Extract education from resume"""
        response = self.model.invoke(
            self.prompt.format(
                resume=resume
            )
        )
        
        educations = []
        try:
            # Extract JSON from the response
            text_content = response.content
            # Find JSON array using regex
            matches = re.search(r'(\[.*\])', text_content, re.DOTALL)
            if matches:
                json_str = matches.group(1)
                # Parse the JSON
                education_list = json.loads(json_str)
                
                # Parse each education entry
                for edu_data in education_list:
                    try:
                        edu = Education(**edu_data)
                        educations.append(edu)
                    except Exception as e:
                        print(f"Error parsing single education entry: {e}")
            else:
                # Try to parse as a single object
                try:
                    edu = self.single_parser.parse(text_content)
                    educations.append(edu)
                except Exception as e:
                    print(f"Error parsing as single education entry: {e}")
        except Exception as e:
            print(f"Error parsing education: {e}")
            
        return educations

class SkillsExtractor:
    """Agent to extract skills information from a resume"""
    
    def __init__(self):
        self.model = get_openai_model()
        self.single_parser = PydanticOutputParser(pydantic_object=Skill)
        self.list_parser = PydanticOutputParser(pydantic_object=SkillList)
        
        self.prompt = create_prompt("""
        You are an AI assistant that extracts skills information from resumes.
        
        Resume:
        {resume}
        
        Job Description:
        {job_description}
        
        Extract all skills from this resume. Return a list of skills, for each skill, provide:
        - Name of the skill
        - Category (technical, soft, domain)
        - Estimated proficiency level
        - Relevance score (0-1) to the provided job description
        
        Format your response as a JSON list of objects where each object represents one skill.
        
        Example format:
        [
            {{
                "name": "Skill Name",
                "category": "Category",
                "level": "Proficiency Level",
                "relevance": 0.8
            }},
            ...
        ]
        """)
        
    def extract(self, resume: str, job_description: str) -> List[Skill]:
        """Extract skills from resume"""
        response = self.model.invoke(
            self.prompt.format(
                resume=resume,
                job_description=job_description
            )
        )
        
        skills = []
        try:
            # Extract JSON from the response
            text_content = response.content
            # Find JSON array using regex
            matches = re.search(r'(\[.*\])', text_content, re.DOTALL)
            if matches:
                json_str = matches.group(1)
                # Parse the JSON
                skill_list = json.loads(json_str)
                
                # Parse each skill
                for skill_data in skill_list:
                    try:
                        skill = Skill(**skill_data)
                        skills.append(skill)
                    except Exception as e:
                        print(f"Error parsing single skill: {e}")
            else:
                # Try to parse as a single object
                try:
                    skill = self.single_parser.parse(text_content)
                    skills.append(skill)
                except Exception as e:
                    print(f"Error parsing as single skill: {e}")
        except Exception as e:
            print(f"Error parsing skills: {e}")
            
        return skills 