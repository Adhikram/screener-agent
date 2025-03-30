"""Model configurations for the AI Resume Reviewer"""
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

def get_openai_model(model_name="gpt-4-turbo", temperature=0):
    """Get OpenAI model instance"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=api_key,
    )

def create_langsmith_client():
    """Create LangSmith client for monitoring"""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        raise ValueError("LANGSMITH_API_KEY not found in environment variables")
    
    return Client(api_key=api_key)

def create_prompt(template):
    """Create a prompt from template"""
    return ChatPromptTemplate.from_template(template) 