from fastapi import FastAPI
import requests
import json
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from typing import List

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def getAccess_token():
    url = 'https://id.trimble.com/oauth/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic IGNjMDliMDc1LWNhMzMtNGI4Zi05NTJjLWNhM2M3OGRjMjYzMDpjY2I5MTcxMjliMjA0Mjg1YTU1Y2YwMmUzMjE0ODkzYg=='
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': 'trimble-assistant-hackathon'
    }
    response = requests.post(url, headers=headers, data=data)
    access_token = response.json()['access_token']
    # print(response.json()['access_token'])
    return access_token

def writePdf(scrappedDatas):
    combined_text = "\n".join(scrappedDatas)
    # Create a canvas object
    c = canvas.Canvas("output.pdf", pagesize=letter)
    width, height = letter

    # Set a font
    c.setFont("Helvetica", 12)

    # Define a margin
    margin = 40

    # Wrap the text
    wrapped_text = textwrap.wrap(combined_text, width=95)  # Adjust width as necessary

    # Starting position
    y = height - margin

    # Draw the text line by line
    for line in wrapped_text:
        if y < margin:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - margin
        c.drawString(margin, y, line)
        y -= 14  # Adjust line height as necessary

    # Save the PDF
    c.save()


def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def get_response_msg(message:str,token:str):
    print(token)
    url = "https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/agents/webscraper/messages"
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    request_body = {
        "message": message,
        "session_id": "1",
        "stream": False,
        "model_id": "gpt-4"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(request_body))
        print(response.json())
        return response.json()['message']
    except Exception as e:
        print(e)

def Scrap_url(url:str):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content
        text_content = extract_text_from_html(html_content)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    print(text_content)
    return text_content

def CreateIndex(token):
    index_name = "webscraper-ta"
    checkUrl = 'https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/indexes/{index_name}'
    create_url = 'https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/indexes'
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token,
    }
    payload = {
    'id': index_name,
    }
    checkIndex = requests.get(checkUrl, headers=headers)
    if(checkIndex.status_code !=200):
        create_response = requests.post(create_url, headers=headers, json=payload)
        print("Index Creation Response:")
        print(create_response.status_code)
        print(create_response.json())
    return index_name

def CreateAgent(index_name,token):
    #create agent
    # Define the URL for the API endpoint
    agent_id = "webscraper"
    url = "https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/agents"

    # Define the payload
    payload = {
        "owners": [],
        "viewers": [],
        "id": agent_id,
        "name": "TrimbleAssistantWebScraper",
        "type": "BaseQuestionAnswerAgent",
        "description": "Used for web scraping",
        "system_prompt": """
        You are a helpful assistant. You are helping a user do web scraping. Accept a URL first and then answer user queries based on data from URL.
        Be brief in your answers.

        Sources:
        {sources}
        """,
        "search_config": {
            "use_vector": True,
            "query_prompt_template": """
            Below is a history of the conversation so far,
            and a new question asked by the user that needs to be answered by searching in a knowledge base.
            Generate a search query based on the conversation and the new question.

            Chat History:
            {chat_history}

            Question:
            {question}
            """,
            "index_name": index_name
        },
        "llm_config": {
            "temperature": 0.2,
            "max_tokens": 800,
            "default_model": "gpt-4"
        },
        "publish": "internal"
    }

    # Set the headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    # Make the request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Print the response
    print(response.status_code)
    print(response.json())
    if response.status_code == 200:
        return agent_id
    else:
        return ''


def DeleteIndex(index_name,access_token):
    #delete index
    # Define the URL for the API endpoint
    url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/indexes/{index_name}"

    # Set the headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    # Make the request
    response = requests.delete(url, headers=headers)

    # Print the response
    print(response.status_code)

    if response.status_code == 204:
        print("Index deleted successfully")
        return True
    else:
        print("Problem in deleting the index")
        return False

def SetIndexData(token,index_name):
    loader = PyPDFLoader("./output.pdf")
    pages = loader.load()

    recursive_text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=600,
    chunk_overlap=125
    )
    print(index_name)
    recursive_text_splitter_chunks = recursive_text_splitter.split_documents(pages)
    url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/indexes/{index_name}/records"
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    request_body = [
        {
            "content": chunk.page_content,
            "file_id": chunk.metadata.get('source'),
        }
        for chunk in recursive_text_splitter_chunks
    ]

    try:
        response = requests.post(url, headers=headers, data=json.dumps(request_body))
        print(response.json())

    except Exception as e:
        print(e)


@app.get("/message")
def read_root():
    access_token = getAccess_token()
    return access_token

@app.get("/qaWithBot/{req}")
def qa_with_gpt(req:str):
    token = getAccess_token()
    response = get_response_msg(req,token)
    return response

class InputData(BaseModel):
    urls:List[str]
    
@app.post("/geturlsummary/")
def getUrlSummary(urls: InputData):
    print(urls)
    token = getAccess_token()
    scrappedDatas = []
    for url in urls.urls:
        scrappedData = Scrap_url(url)
        scrappedDatas.append(scrappedData)

    print("pdf",scrappedDatas)
    writePdf(scrappedDatas)
    print("Completed pdf")

    if(scrappedData):
        createdIndex = CreateIndex(token)
    if(createdIndex != ''):
        SetIndexData(token,createdIndex)
    # CreateAgent("webscraper-ta",token)
    return get_response_msg("Give me the summary of the document",token)


@app.get("/deleteIndex")
def deleteRoute():
    token = getAccess_token()
    return DeleteIndex("webscraper-ta",token) 

        
    
    

