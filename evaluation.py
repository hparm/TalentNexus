from flask import Flask, request, jsonify
import os
from db.db_helper import *
from utils import extract_resume, process_answers
from dotenv import load_dotenv
import os
import anthropic
import threading
from agents.WorkflowOrchestrator import WorkflowOrchestrator

app = Flask(__name__)

load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')


@app.route('/')
def home():
    

    #Get test candidate & role
    #email = "hector.parmantier@wanadoo.fr"
    #title = "AI Operations Manager"
    #candidate = get_candidate(email)
    #role = get_role(title)

    # Create & run orchestrator
    #orchestrator = WorkflowOrchestrator(client)
    #result = orchestrator.process_new_candidate(candidate, role)
    return "Welcome to the Talent Nexus API!"


def print_banner():
    banner = """
    +--------------------------------------------------------------------+
    |                                                                    |
    |   _______    _             _     _   _                             |
    |  |__   __|  | |           | |   | \ | |                            |
    |     | | __ _| | ___ _ __ _| |_  |  \| | _____  ___  _   _ ___      |
    |     | |/ _` | |/ _ \ '_ \_   _| | . ` |/ _ \ \/ / | | | / __|     |
    |     | | (_| | |  __/ | | || |_  | |\  |  __/>  <  | |_| \__ \     |
    |     |_|\__,_|_|\___|_| |_| \__| |_| \_|\___/_/\_\  \__,_|___/     |
    |                                                                    |
    |   v1.0.0                Agent-powered Talent Screening API         |
    +--------------------------------------------------------------------+
    """
    print(banner)

    

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json.copy()  # Make a copy of the data
    
    # Store the data for processing
    if 'form_response' in data and 'answers' in data['form_response']:
        # Start processing in background thread
        import threading
        thread = threading.Thread(target=process_webhook_data, args=(data,))
        thread.daemon = True
        thread.start()
        
        # Return success immediately
        return jsonify(status="success", message="Processing started"), 200
    else:
        return jsonify(status="error", message="Invalid data format"), 400

def process_webhook_data(data):
    """Process webhook data in background thread"""
    try:
        # Extract answers from the webhook data
        answers = data['form_response']['answers']
        print("#"*50 + " FORM ANSWERS RECEIVED " + "#"*50)
        print("PROCESSING ANSWERS...")
        response = process_answers(answers)
        print("Processed response:", response)
        
        # Extract resume URL and convert to text
        candidate = get_candidate(response["email"])
        role = get_role(response["role_title"])

        # Create & run orchestrator
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("#"*50 + " LAUNCHING AGENTS... " + "#"*50)
        orchestrator = WorkflowOrchestrator(client)
        result = orchestrator.process_new_candidate(candidate, role)

        print("Webhook processing completed successfully")

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")

if __name__ == '__main__':
    print_banner()
    app.run(host='0.0.0.0', port=5001, debug=False)