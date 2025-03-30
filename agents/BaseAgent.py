# Recorder Agent class
import json
import datetime
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
LLM_MODEL = os.getenv('LLM_MODEL')

def log_step(message):
    """Print a timestamped log message"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class Agent:
    def __init__(self, client):
        self.client = client
    
    def _call_llm(self, prompt, max_tokens=2500):
        """Make a call to the LLM API"""
        try:
            log_step(f"{self.__class__.__name__}: 🔄 Sending request to Claude API...")
            message = self.client.messages.create(
                model=LLM_MODEL,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            log_step(f"{self.__class__.__name__}: Received response from Claude API")
            return message.content[0].text
        except Exception as e:
            log_step(f"{self.__class__.__name__}: Error calling LLM: {e}")
            raise