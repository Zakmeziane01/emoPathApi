from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Optional, Any
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


user_infos: Dict[str, dict] = {}


class UserInfo(BaseModel):
    userId: str 
    age: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[str] = None


class AnalysisReport(BaseModel):
    userId:  str
    report: str




@app.get("/")
def read_root():
    return {"message": "Hello, World!"}



@app.post("/checkIn_optimization_entire/")
async def receive_check_in(data: UserInfo):
    data_info = data.dict()

    return {
        "message": "Check-in and plan adjustment completed successfully!",
        "data_info": data_info,
    
    }






