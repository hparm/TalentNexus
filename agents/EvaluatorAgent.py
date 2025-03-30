import json
import datetime
from .BaseAgent import Agent

def log_step(message):
    """Print a timestamped log message"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


class EvaluatorAgent(Agent):
    def evaluate(self, candidate, role, review=None):
        """Evaluates candidate based on resume and job requirements"""
        log_step("EVALUATOR: Starting evaluation")
        
        guidance_section = ""
        if review:
            feedback = review.get('feedback', '')
            improvement_areas = review.get('improvement_areas', [])
            
            if feedback:
                log_step(f"📝 Incorporating feedback: {feedback[:200]}...")
                guidance_section += f"""
                Previous review feedback:
                {feedback}
                """
            
            if improvement_areas and isinstance(improvement_areas, list) and len(improvement_areas) > 0:
                log_step(f"📋 Incorporating improvement areas: {', '.join(improvement_areas)}")
                guidance_section += "\nSpecific areas to improve:\n"
                for i, area in enumerate(improvement_areas):
                    guidance_section += f"{i+1}. {area}\n"
            
            if guidance_section:
                guidance_section += "\nPlease address this feedback in your updated evaluation."
        
        current_date = datetime.datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        requirements_formatted = role["description"]
        
        prompt = f"""
        I'm evaluating a candidate for a {role['title']} position.

        Job Requirements:
        {requirements_formatted}
        
        Candidate Information:
        Name: {candidate['first_name']} {candidate['last_name']}
        
        Resume:
        {candidate["resume"]}
        
        {guidance_section}
        
        Today's exact date is {current_month}/{current_date.day}/{current_year}. Use this for precise experience calculations.
        
        Please evaluate this candidate with the following approach:
        
        1. Be precise in calculating years of experience:
           - For entries like "2024-Present", you must interpret this cautiously:
              * If no month is specified, assume it started in January of that year
              * For present positions, calculate duration up to today's exact date
              * Express partial years with decimal precision (e.g., 1.3 years)
           - Sum experience across ALL positions in the resume
           - Make calculations explicit (e.g., "Position A: 2.3 years, Position B: 1.5 years, Total: 3.8 years")
        
        2. Identify transferable skills:
           - Look for skills that apply to the requirements even if from different industries
           - Consider how domain knowledge from one field might transfer to this role
           - Evaluate adjacent technologies or methodologies that demonstrate relevant capabilities
        
        3. Consider depth and quality of experience:
           - Assess leadership roles and their relevance
           - Look for progression in responsibilities
           - Evaluate projects and achievements that demonstrate required capabilities
        
        Please evaluate this candidate on the following dimensions on a scale of 1-10:
        1. Technical Skills Match
        2. Experience Level
        3. Domain Knowledge
        4. Culture Fit
        5. Overall Match Percentage
        
        SCORING GUIDELINES FOR ALL DIMENSIONS:
        - 9-10: Exceptional match with direct, extensive experience/skills
          • Has direct, specific experience in this exact dimension
          • All key requirements are met or exceeded
          • If a score of 10 is warranted by the evidence and no gaps are identified, do not artificially hold back
          • A score of 9 indicates a very strong match with perhaps one minor limitation

        - 7-8: Strong match with relevant experience/skills and minor gaps
          • Has most of the required experience/skills
          • May have adjacent or transferable rather than direct experience
          • Minor gaps may exist but are offset by strengths in related areas

        - 5-6: Moderate match with partial experience/skills and notable gaps
          • Has some relevant experience/skills but lacks others
          • Experience may be limited in depth or recency
          • Transferable skills partially compensate for direct experience gaps

        - 3-4: Basic match with limited experience/skills and significant gaps
          • Limited relevant experience/skills
          • Several significant gaps exist
          • Would require substantial development in this area

        - 1-2: Poor match with minimal to no relevant experience/skills
          • Little to no relevant experience/skills
          • Critical gaps that cannot be easily overcome
          • Doesn't meet fundamental requirements

        BALANCED SCORING APPROACH:
        - Score based on the evidence, not an idealized perfect candidate
        - If you cannot identify any specific gaps or weaknesses, use the higher end of the range
        - If the candidate exceeds requirements in a dimension, this warrants a score of 10
        - Explicitly state any gaps you identify, and ensure scores reflect these gaps
        - Be willing to give scores of 10 when justified - it means "fully meets or exceeds all requirements"
        - For each score below 10, specifically explain what prevented a higher score

        For each dimension, provide:
        - The score (1-10) or (1-100) for Overall Match Percentage
        - Detailed evidence from the resume supporting this score
        - Any transferable skills or experience that contribute to this dimension
        - A calculation of years of relevant experience where applicable
        
        CRITICAL: Your response MUST be a valid JSON object with no formatting errors. 
        Ensure all keys and string values are in double quotes.
        Do not include any explanations or markdown formatting outside the JSON object.
        """
        
        response_text = self._call_llm(prompt, max_tokens=1500)
        
        # Extract JSON from response
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            evaluation = json.loads(json_str)
            log_step("✅ Successfully parsed evaluation results")
            
            # Print summary of evaluation
            log_step("Evaluation Summary:")
            for key, value in evaluation.items():
                if isinstance(value, (int, float)) and key != "error":
                    log_step(f"  - {key}: {value}")
            
            return evaluation
        except Exception as e:
            log_step(f"❌ Error parsing evaluator response: {e}")
            return {"error": "Failed to parse evaluation"}