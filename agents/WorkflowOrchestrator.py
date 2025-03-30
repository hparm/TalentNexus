from .EvaluatorAgent import EvaluatorAgent
from .ReviewerAgent import ReviewerAgent
from .RecorderAgent import RecorderAgent
from .BaseAgent import Agent

import json
import datetime
import os

def log_step(message):
    """Print a timestamped log message"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class WorkflowOrchestrator:
    def __init__(self, anthropic_client):
        self.anthropic_client = anthropic_client
        self.evaluator = EvaluatorAgent(anthropic_client)
        self.reviewer = ReviewerAgent(anthropic_client)
        self.recorder = RecorderAgent(anthropic_client)
        self.max_iterations = 3
    
    def process_new_candidate(self, candidate, role):
        """Process a candidate for a specific role"""
        log_step(f"🚀 ORCHESTRATOR: Starting workflow for candidate {candidate['email']} and role {role['title']}")
        
        # Start evaluation process
        result = self.evaluate_candidate(candidate, role)
        
        return result
    
    def evaluate_candidate(self, candidate, role):
        """Evaluate a candidate for a specific role"""
        log_step(f"🔄 ORCHESTRATOR: Evaluating candidate {candidate['email']} for role {role['title']}")
        
        # Initial evaluation
        log_step("🔄 Starting initial evaluation...")
        evaluation = self.evaluator.evaluate(candidate, role)
        
        log_step("📊 Initial Evaluation:")
        print(json.dumps(evaluation, indent=2))
        
        # Reviewer-evaluator loop
        current_iteration = 1
        review_history = []
        
        while current_iteration <= self.max_iterations:
            log_step(f"🔄 REVIEW CYCLE: Iteration #{current_iteration} of {self.max_iterations}")
            
            # Get review
            review = self.reviewer.review(evaluation, candidate, role, current_iteration)
            review_history.append(review)
            
            # Print review
            log_step(f"🔍 Review #{current_iteration}:")
            print(json.dumps(review, indent=2))
            
            # Check if approved
            if review.get('status') == 'approved':
                log_step(f"✅ Evaluation APPROVED after {current_iteration} iterations!")
                break
                
            # Print warning if this is the final iteration
            if current_iteration == self.max_iterations:
                log_step(f"⚠️ Max iterations ({self.max_iterations}) reached. Performing final evaluation.")
    
                
            # Get improved evaluation based on review
            log_step("🔄 Getting improved evaluation based on feedback...")
            evaluation = self.evaluator.evaluate(
                candidate, 
                role,
                review
            )
            
            # Print updated evaluation
            log_step(f"📊 Updated Evaluation (Iteration #{current_iteration + 1}):")
            print(json.dumps(evaluation, indent=2))
            
            current_iteration += 1
        
        current_iteration = 3 if current_iteration > 3 else current_iteration
        # Record the final evaluation
        log_step("🗃️ Recording final evaluation...")
        self.recorder.record_evaluation(
            candidate,
            role,
            evaluation,
            review_history,
            current_iteration
        )
        
        #log_step(f"✅ ANALYSIS COMPLETE: Candidate {candidate['email']} processed after {current_iteration} iterations")
        
        
        return evaluation