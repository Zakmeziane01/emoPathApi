from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
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

@app.post("/first_time/")
async def receive_first_time(data: FamilyData):
    # Here, 'data' contains the parent and children data
    data_info = data.dict()  # Converting Pydantic model to a dictionary

    # You can apply any logic to process the received data here
    print("Received data:", data_info)

    # Respond back with a success message and the received data
    return {
        "message": "First time check-in and plan adjustment completed successfully!",
        "data_info": data_info,
    }
