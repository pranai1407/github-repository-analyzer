from fastapi import FastAPI
from backend.services.repository_service import RepositoryService

app = FastAPI()

service = RepositoryService()


@app.get("/")
def home():
    return {
        "message": "GitHub Repository Analyzer API"
    }


@app.post("/analyze")
def analyze_repository(repo_url: str):

    return service.analyze_repository(repo_url)


@app.post("/ask")
def ask_repository_question(repo_url: str, question: str):

    return service.ask_question(repo_url, question)