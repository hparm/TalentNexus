# This file marks the 'agents' directory as a Python package
# You can leave it empty or use it to expose specific modules/classes

# Optional: Expose commonly used classes for easier imports
from .BaseAgent import Agent
from .EvaluatorAgent import EvaluatorAgent
from .ReviewerAgent import ReviewerAgent
from .RecorderAgent import RecorderAgent
from .WorkflowOrchestrator import WorkflowOrchestrator

# This allows users to do:
# from agents import EvaluatorAgent, WorkflowOrchestrator
# Instead of:
# from agents.EvaluatorAgent import EvaluatorAgent