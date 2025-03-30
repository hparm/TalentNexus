import json
import datetime
from .BaseAgent import Agent

def log_step(message):
    """Print a timestamped log message"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class ReviewerAgent(Agent):
    def review(self, evaluation, candidate, role, iteration):
        """Reviews the evaluation for thoroughness and accuracy"""
        log_step(f"🔍 REVIEWER: Starting review (Iteration #{iteration})")
        
        requirements_formatted = role["description"]
        
        current_date = datetime.datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        prompt = f"""
        You are a hiring manager reviewing an AI evaluation of a candidate for a {role['title']} position.
        Your task is to ensure the evaluation is accurate, well-reasoned, and fair.

        Today's exact date is {current_month}/{current_date.day}/{current_year}.

        Job Requirements:
        {requirements_formatted}
        
        AI Evaluation (Iteration #{iteration}):
        {json.dumps(evaluation, indent=2)}
        
        Original Resume Text:
        {candidate["resume"]}
        
        Please review the evaluation with these principles in mind:
        
        1. Experience calculations should be approximately correct:
           - Small differences in decimal places (±0.1 years) are acceptable and should NOT be flagged
           - Only flag experience calculation errors if they're off by 0.5+ years or miss entire positions
           - For entries like "2024-Present", approximate calculations are sufficient
           - Focus on whether all relevant positions are included rather than decimal precision
           - The exact method of calculation isn't important as long as the result is reasonable

        2. Transferable skills should be appropriately recognized:
           - Consider how skills from different contexts apply to this role
           - Verify that domain knowledge is evaluated fairly across industries
           - Check that adjacent or related technologies are recognized appropriately
        
        3. The evaluation should be consistent and logical:
           - Scores should match the supporting evidence provided
           - There should be no contradictions in the assessment
           - The overall match percentage should align with the individual dimension scores
        
        4. Scoring must be consistent with evidence:
           - Verify that each score is justified by the evidence presented
           - Check that high scores (8-10) are supported by strong evidence showing how requirements are met
           - Check that lower scores clearly identify specific gaps or weaknesses
           - Flag any inconsistencies between the evidence provided and the score assigned
           - Ensure the evaluator is neither artificially reluctant to assign high scores nor inflating scores beyond what the evidence supports
           
        5. All dimension scores must be consistent with evidence and gaps:
           - Verify that scores align with the evidence provided
           - Scores of 9-10 are appropriate when the candidate has direct, specific experience meeting all requirements
           - If the evaluation identifies gaps, the score should reflect these gaps
           - Check that the evaluator isn't unnecessarily withholding high scores when no gaps are identified
           - Be equally vigilant about both score inflation and deflation
           - A score of 10 is warranted when the candidate fully meets or exceeds requirements, not only for theoretical "perfect" candidates
           - Flag inconsistencies in either direction - both when scores are too high given identified gaps AND when scores are too low despite strong evidence

        SCORING GUIDELINES:
        - A score of 10/10 means the candidate fully meets or exceeds all requirements in this dimension with no identifiable gaps
        - A score of 8-9/10 indicates strong alignment with minor gaps that should be explicitly identified
        - A score of 5-7/10 indicates moderate alignment with several notable gaps
        - Every score should be justified with specific evidence
        
        If the evaluation is thorough, accurate, and fair, respond with:
        {{
            "status": "approved",
            "comments": "Your specific comments on the strengths of this evaluation"
        }}
        
        If the evaluation needs improvement, respond with:
        {{
            "status": "needs_improvement",
            "feedback": "Clear, specific feedback on what needs to be corrected or improved",
            "improvement_areas": ["List specific areas that need attention"]
        }}
        
        For the first iteration, be especially attentive to areas that could be enhanced,
        but judge based on substantive issues rather than seeking problems unnecessarily.
        Focus on improvements that would significantly change the assessment or scores.
        
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
            review = json.loads(json_str)
            
            log_step(f"📝 Review Status: {review.get('status', 'unknown')}")
            if review.get('status') == 'approved':
                log_step(f"✅ Review approved with comment: {review.get('comments', '')[:100]}...")
            elif review.get('status') == 'needs_improvement':
                log_step(f"🔄 Improvements needed: {review.get('feedback', '')[:100]}...")
            
            return review
        except Exception as e:
            log_step(f"❌ Error parsing reviewer response: {e}")
            return {"status": "error", "message": str(e)}