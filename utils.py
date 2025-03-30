import requests
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
from docx import Document

load_dotenv()
TYPEFORM_API_KEY = os.getenv('TYPEFORM_API_KEY')

def extract_resume(url):
    pdf_file_path = url
    write_path = "/downloads/" + pdf_file_path.split("/")[-1]
    need_conversion = pdf_file_path.lower().endswith('.pdf')
    
    #Download file
    headers = {"Authorization": f"Bearer {TYPEFORM_API_KEY}"}
    response = requests.get(pdf_file_path, headers=headers)
    if response.status_code == 200:
        with open(write_path, "wb") as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
        exit()
    
    #Convert to pdf
    text = ""

    if need_conversion:
        try:
            # Read the downloaded PDF to ensure it's a valid PDF
            with open(write_path, "rb") as f:
                reader = PdfReader(f)
                # Loop through all the pages and extract text
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text()

        except Exception as e:
            print(f"Error reading PDF: {e}")
            exit()
    else:
        doc = Document(write_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
            
    return text

def process_answers(answers):
    record = {}
    for i in range(len(answers)):
        if i == 0:
            record["role_title"] = answers[i]["choice"]['label']
        elif i == 1:
            record["first_name"] = answers[i]["text"]
        elif i == 2:
            record["last_name"] = answers[i]["text"]
        else:
            record[answers[i]["type"]] = answers[i][answers[i]["type"]]
    return record
