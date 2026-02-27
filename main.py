import os
import sys
import traceback
from io import StringIO
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# --- App Setup ---
app = FastAPI()

# CORS lets browsers/testers talk to your API from any website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request & Response Models ---
class CodeRequest(BaseModel):
    code: str  # The Python code sent by the user

class CodeResponse(BaseModel):
    error: List[int]   # Line numbers with errors (empty if no error)
    result: str        # The exact output or traceback

# --- Part 1: Tool Function ---
def execute_python_code(code: str) -> dict:
    """Runs the code and captures whatever it prints (or crashes with)."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()  # Redirect print() output to a "fake" console

    try:
        exec(code)  # Actually run the code
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}

    except Exception:
        output = traceback.format_exc()  # Capture the full error message
        return {"success": False, "output": output}

    finally:
        sys.stdout = old_stdout  # Always restore the real console

# --- Part 2: AI Error Analysis ---
def analyze_error_with_ai(code: str, traceback_output: str) -> List[int]:
    """Asks Gemini to look at the broken code and find which line(s) caused the error."""

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = f"""
Analyze this Python code and its error traceback.
Identify the line number(s) where the error occurred.

CODE:
{code}

TRACEBACK:
{traceback_output}

Return the line number(s) where the error is located.
"""

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "error_lines": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.INTEGER)
                    )
                },
                required=["error_lines"]
            )
        )
    )

    # Parse the AI's JSON response into a Python object using Pydantic
    class ErrorAnalysis(BaseModel):
        error_lines: List[int]

    result = ErrorAnalysis.model_validate_json(response.text)
    return result.error_lines

# --- Part 3: The Endpoint ---
@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(request: CodeRequest):
    # Step 1: Run the code
    execution = execute_python_code(request.code)

    # Step 2: If it worked, return the output with no errors
    if execution["success"]:
        return CodeResponse(error=[], result=execution["output"])

    # Step 3: If it crashed, ask AI to find the broken line(s)
    error_lines = analyze_error_with_ai(request.code, execution["output"])

    return CodeResponse(error=error_lines, result=execution["output"])
    