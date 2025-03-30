# TalentNexus

TalentNexus is an AI-powered talent screening API that automates the evaluation of job candidates using multiple AI agents.

## Description

TalentNexus integrates with Typeform for candidate submissions and uses Claude AI to evaluate candidates against job requirements. The system employs multiple specialized agents:

- EvaluatorAgent: Analyzes candidate resumes against job requirements
- ReviewerAgent: Reviews and validates evaluations
- RecorderAgent: Records evaluation results
- WorkflowOrchestrator: Coordinates the evaluation workflow

## Prerequisites

- Python 3.x
- Anthropic API key
- Typeform API key
- SQLite database

## Installation

1. Clone the repository
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- typeform
- sqlite3
- anthropic
- pypdf2
- python-docx

## Environment Setup

Create a `.env` file in the root directory with:

```python
LLM_MODEL=claude-3-7-sonnet-20250219 
ANTHROPIC_API_KEY=your_api_key 
TYPEFORM_API_KEY=your_api_key
```


## Database

The project uses SQLite database (`db/talentnexus.db`) with the following main tables:
- candidates
- roles

## Usage

### Typeform Integration

The system accepts candidate submissions through Typeform with fields for:
- Role selection
- First name
- Last name
- Email
- Resume upload (PDF/DOC)



### API Endpoints

- `/`: Welcome endpoint
- `/webhook`: Handles Typeform submission webhooks

### Running the Application

```python
# Create & run orchestrator
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
orchestrator = WorkflowOrchestrator(client)
result = orchestrator.process_new_candidate(candidate, role)
```

## Project Structure

├── agents/
│   ├── __init__.py
│   ├── BaseAgent.py
│   ├── EvaluatorAgent.py
│   ├── ReviewerAgent.py
│   └── RecorderAgent.py
├── db/
│   ├── talentnexus.db
│   └── db_helper.py
├── utils.py
├── evaluation.py
├── dashboard.py
├── requirements.txt
└── .env

## Features

- PDF and DOC resume parsing
- Automated candidate evaluation
- Multi-stage review process
- Precise experience calculation
- Standardized scoring system (1-10 scale)