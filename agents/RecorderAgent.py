# Recorder Agent class
import json
import time
import datetime
from db.db_helper import create_evaluation
from .BaseAgent import Agent

def log_step(message):
    """Print a timestamped log message"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class RecorderAgent(Agent):
    def __init__(self, client):
        super().__init__(client)
    
    def parse_evaluation(self, evaluation, candidate, review_history):
        """Parse potentially unstructured evaluation into structured data using LLM"""
        log_step("🔍 RECORDER: Parsing evaluation results")
        
        # Create a prompt that asks the LLM to extract structured data
        prompt = f"""
        I need to extract structured data from an AI-generated candidate evaluation.
        
        Here is the raw evaluation:
        {json.dumps(evaluation, indent=2)}
        
        And here is some context about the review process:
        - Review iterations: {len(review_history)}
        - Final review status: {review_history[-1].get('status', 'unknown') if review_history else 'unknown'}
        - Candidate: {candidate['email']}
        
        Please extract the following information and return it as a JSON object:
        {{
            "technical_skills": [score between 0-10],
            "experience_level": [score between 0-10],
            "domain_knowledge": [score between 0-10],
            "culture_fit": [score between 0-10],
            "overall_match": [percentage between 0-100],
            "analysis_notes": [concise summary of strengths, weaknesses, and fit]
        }}
        
        If any field is missing from the raw evaluation, please make a reasonable inference based on the available information.
        Ensure all numeric fields are properly formatted as numbers, not strings.
        
        CRITICAL: Your response MUST be a valid JSON object with no formatting errors. 
        Ensure all keys and string values are in double quotes.
        Do not include any explanations or markdown formatting outside the JSON object.
        """
        
        response_text = self._call_llm(prompt, max_tokens=1000)
        
        # Extract JSON from response
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            parsed_data = json.loads(json_str)
            log_step("✅ Successfully parsed evaluation into structured data")
            
            # Print summary
            log_step("📊 Parsed Evaluation Summary:")
            for key, value in parsed_data.items():
                if isinstance(value, (int, float)):
                    log_step(f"  - {key}: {value}")
            
            return parsed_data
        except Exception as e:
            log_step(f"❌ Error parsing evaluation data: {e}")
            return None
    
    def record_evaluation(self, candidate, role, evaluation, review_history, iterations):
        """Parse and record evaluation results in the database"""
        log_step("🗃️ RECORDER: Processing and storing evaluation results")
        
        # Parse the evaluation into structured data
        parsed_data = self.parse_evaluation(evaluation, candidate, review_history)
        
        if not parsed_data:
            log_step("❌ Failed to parse evaluation data, using raw data")
            parsed_data = evaluation
        
        # Add review history as part of analysis notes if not already there
        if 'analysis_notes' not in parsed_data or not parsed_data['analysis_notes']:
            parsed_data['analysis_notes'] = f"Review process took {iterations} iterations."
        else:
            parsed_data['analysis_notes'] += f"\n\nReview process took {iterations} iterations."
        
        # Extract candidate and role IDs
        candidate_id = candidate.get('id', 0)
        role_id = role.get('id', 0)
        
        log_step(f"📝 Recording evaluation for candidate {candidate['email']} and role {role['title']}")
        
        try:
            
            recommendation = None
            # Update candidate status based on match score
            if 'overall_match' in parsed_data:
                match_score = parsed_data['overall_match']
                if match_score >= 75:
                    recommendation = "Move to interview"
                elif match_score >= 60:
                    recommendation = "Further review"
                else:
                    recommendation = "Do not proceed"
                    
            # Create a dict with only the fields needed for the database
            evaluation_data = {
                'candidate_id': candidate_id,
                'role_id': role_id,
                'technical_skills': parsed_data.get('technical_skills', 0),
                'experience_level': parsed_data.get('experience_level', 0),
                'domain_knowledge': parsed_data.get('domain_knowledge', 0),
                'culture_fit': parsed_data.get('culture_fit', 0),
                'overall_match': parsed_data.get('overall_match', 0),
                'recommendation': recommendation,
                'analysis_notes': parsed_data.get('analysis_notes', '')
            }
            
            # Store the structured data in the database using the db_helper function
            evaluation_id = create_evaluation(candidate_id, role_id, evaluation_data)
            
            log_step(f"✅ Evaluation recorded with ID: {evaluation_id}")
            return evaluation_id
        
        except Exception as e:
            log_step(f"❌ Error storing evaluation in database: {e}")
            return None
