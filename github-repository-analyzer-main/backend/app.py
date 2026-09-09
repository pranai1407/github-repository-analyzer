from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from backend.services.repository_service import RepositoryService


app = FastAPI(
    title="GitHub Repository Analyzer API",
    description="API for analyzing GitHub repositories using repository statistics and AI.",
    version="1.0.0",
)


# Initialize the main application service.
service = RepositoryService()


@app.get("/")
def home():
    """Health check / API information endpoint."""

    return {
        "message": "GitHub Repository Analyzer API",
        "status": "running",
    }


@app.post("/analyze")
def analyze_repository(repo_url: str):
    """
    Analyze a GitHub repository.

    The repository URL is passed to RepositoryService, which handles
    cloning and analysis.
    """

    if not repo_url or not repo_url.strip():
        raise HTTPException(
            status_code=400,
            detail="GitHub repository URL is required.",
        )

    try:
        return service.analyze_repository(repo_url.strip())

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Repository analysis failed: {exc}",
        ) from exc


@app.post("/ask")
def ask_repository_question(
    repo_url: str,
    question: str,
):
    """
    Ask an AI question about a GitHub repository.
    """

    if not repo_url or not repo_url.strip():
        raise HTTPException(
            status_code=400,
            detail="GitHub repository URL is required.",
        )

    if not question or not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question is required.",
        )

    try:
        return service.ask_question(
            repo_url.strip(),
            question.strip(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to answer the question: {exc}",
        ) from exc


@app.post("/generate-report")
def generate_report(repo_url: str):
    """
    Generate and return a PDF report for a GitHub repository.
    """

    if not repo_url or not repo_url.strip():
        raise HTTPException(
            status_code=400,
            detail="GitHub repository URL is required.",
        )

    try:
        filename = service.generate_pdf_report(
            repo_url.strip()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {exc}",
        ) from exc

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL.",
        )

    report_path = Path(filename)

    if not report_path.exists() or not report_path.is_file():
        raise HTTPException(
            status_code=500,
            detail="The PDF report could not be created.",
        )

    return FileResponse(
        path=str(report_path),
        filename=report_path.name,
        media_type="application/pdf",
    )