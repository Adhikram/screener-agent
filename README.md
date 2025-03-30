# AI Resume Reviewer

An AI-powered resume reviewer that analyzes resumes against job descriptions to extract key parameters and evaluate their match. Built using LangGraph for workflow orchestration, Swarm Agents for parallel processing, and LangSmith for monitoring and optimization.

## Features

- **Resume Analysis**: Extract work experience, education, and skills from resumes
- **Job Matching**: Compare resume contents with job requirements
- **Scoring**: Generate compatibility scores and personalized feedback
- **API Access**: Easy-to-use API endpoint for integration

## Architecture

- **LangGraph**: Manages the workflow execution with parallel processing
- **Swarm Agents**:
  - Experience Extractor: Retrieves work experience details
  - Education Extractor: Extracts degrees and certifications
  - Skills Extractor: Identifies relevant skills
  - Match Analyzer: Compares extracted data with job requirements
  - Score Generator: Computes compatibility score and feedback
- **LangSmith**: Provides observability, debugging, and performance tracking

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key
- LangSmith API key (optional, for monitoring)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/resume-reviewer.git
   cd resume-reviewer
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your API keys

### Running the Application

There are two ways to use the application:

#### 1. Using the Command-Line Interface

1. Create two text files in the project root:
   - `resume.txt`: Containing the resume content
   - `jd.txt`: Containing the job description content

2. Run the main script:
   ```
   python main.py
   ```

3. Check the output in the console and in the generated `result.json` file

#### 2. Using the API Server

Start the API server:
```
python run_api.py
```

The API will be available at http://localhost:8000 

## API Usage

### Review a Resume

```
POST /review
```

Request body:
```json
{
  "resume": "Resume text content...",
  "job_description": "Job description text content..."
}
```

Response:
```json
{
  "experiences": [...],
  "education": [...],
  "skills": [...],
  "match_analysis": {
    "match_points": [...],
    "gaps": [...],
    "suggestions": [...]
  }
}
```

## Development

### Project Structure

```
resume-reviewer/
├── app/
│   ├── agents/           # Swarm agents for extraction and analysis
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Core workflow and model configurations
│   └── utils/            # Utility functions
├── .env.example          # Example environment variables
├── main.py               # Main entry point for CLI usage
├── requirements.txt      # Project dependencies
├── run_api.py            # Script to run the API server
├── resume.txt            # Sample resume (for CLI usage)
└── jd.txt                # Sample job description (for CLI usage)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 