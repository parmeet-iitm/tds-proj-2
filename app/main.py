"""
Main FastAPI application for the TDS Assignment Solver.
"""

import os
from fastapi import FastAPI, UploadFile, Form, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import shutil
from typing import Optional

from app.question_processor import QuestionProcessor
from app.utils.file_utils import save_upload_file, cleanup_temp_file

# Initialize FastAPI app
app = FastAPI(
    title="TDS Assignment Solver",
    description="AI-powered API for solving TDS graded assignment questions",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get AI Proxy token from environment variable
ai_proxy_token = os.environ.get("AIPROXY_TOKEN")

# Initialize question processor with AI proxy token
processor = QuestionProcessor(ai_proxy_token)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "TDS Assignment Solver API",
        "version": "0.1.0",
        "description": "AI-powered API for solving TDS graded assignment questions",
        "usage": "Send a POST request to /api/ with your question and optional file",
    }


@app.post("/api/")
async def answer_question(
    background_tasks: BackgroundTasks,
    question: str = Form(...),
    file: Optional[UploadFile] = File(None),
):
    """
    Process a question from a TDS graded assignment and provide an answer.

    Parameters:
    - question: The question text from the assignment
    - file: Optional file attachment (e.g., zip, CSV)

    Returns:
    - JSON object with the answer field
    """
    temp_file_path = None

    try:
        # If a file was uploaded, save it temporarily
        if file:
            temp_file_path = await save_upload_file(file)

        # Process the question using the AI-powered question processor
        answer = await processor.process_question(question, temp_file_path)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

    finally:
        # Schedule cleanup of temporary file
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)