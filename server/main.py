from fastapi import FastAPI
import requests
import json
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

# Add CORS middleware to allow all origins
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
    url = "https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/agents/generic/messages"
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

@app.get("/message")
def read_root():
    access_token = getAccess_token()
    return access_token


@app.get("/qaWithBot/{req}")
def qa_with_gpt(req:str):
    token = getAccess_token()
    response = get_response_msg(req,token)
    return response

