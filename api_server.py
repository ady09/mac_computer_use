#!/usr/bin/env python3
"""
Simple HTTP API server for OrcaSheets automation
Runs locally and exposes endpoints for the MCP server to call
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn
import sys
import os
import re
from typing import Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.orcasheets.tool import OrcaSheetsTool

app = FastAPI(title="OrcaSheets Automation API", version="1.0.0")

class AutomationRequest(BaseModel):
    prompt: str
    file_path: Optional[str] = None
    project_name: Optional[str] = None

class AutomationResponse(BaseModel):
    status: str
    result: dict
    message: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "OrcaSheets Automation API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "orcasheets-automation"}

@app.post("/orcasheets/automation", response_model=AutomationResponse)
async def run_orcasheets_automation(request: AutomationRequest):
    """
    Run OrcaSheets automation based on natural language prompt
    """
    try:
        print(f"[API] Received automation request: {request.prompt}")
        
        prompt = request.prompt
        prompt_lower = prompt.lower()
        
        # Extract file path from prompt if not provided
        file_path = request.file_path
        if not file_path:
            if "~/downloads/" in prompt_lower:
                file_match = re.search(r"~/downloads/([\w\.-]+)", prompt_lower)
                if file_match:
                    file_path = f"~/Downloads/{file_match.group(1)}"
            elif "downloads/" in prompt_lower:
                file_match = re.search(r"downloads/([\w\.-]+)", prompt_lower)
                if file_match:
                    file_path = f"~/Downloads/{file_match.group(1)}"
            
            if not file_path:
                file_match = re.search(r"(\w+\.csv)", prompt_lower)
                file_path = f"~/Downloads/{file_match.group(1)}" if file_match else None
        
        # Extract project name if not provided
        project_name = request.project_name
        if not project_name:
            project_match = re.search(r"select ([\w\- ]+) project", prompt_lower)
            project_name = project_match.group(1).strip() if project_match else None
        
        print(f"[API] Extracted: file_path={file_path}, project_name={project_name}")
        
        # Run the automation
        orca_tool = OrcaSheetsTool()
        result = await orca_tool.run_workflow(prompt, file_path, project_name)
        
        print(f"[API] Automation result: {result}")
        
        return AutomationResponse(
            status="success",
            result=result,
            message="Automation completed successfully"
        )
        
    except Exception as e:
        print(f"[API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Automation failed: {str(e)}"
        )

@app.post("/orcasheets/test")
async def test_automation():
    """Test endpoint to verify the API is working"""
    try:
        return {
            "status": "success",
            "message": "Test endpoint working",
            "can_import_tools": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )

if __name__ == "__main__":
    print("[API] Starting OrcaSheets Automation API server...")
    print("[API] Server will be available at: http://localhost:8000")
    print("[API] API docs at: http://localhost:8000/docs")
    
    # Run the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )