from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from fastapi.middleware.cors import CORSMiddleware
import os
from rag import RAGResponse, rag_system_omf

app = FastAPI(title="EmoPath API", 
              description="API for EmoPath family guidance system using RAG technology",
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example response structure
class FamilyData(BaseModel):
    parent: Optional[Dict[str, Any]] = None
    children: Optional[List[Dict[str, Any]]] = []

@app.post("/first_time/", response_model=RAGResponse)
async def receive_first_time(data: FamilyData):
    """
    Process first-time check-in data and provide personalized guidance
    
    This endpoint receives family data and uses a RAG system to provide
    personalized recommendations based on similar case studies.
    """
    data_dict = data.dict()
    response = rag_system_omf(data_dict)
    return response