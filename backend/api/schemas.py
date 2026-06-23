from pydantic import BaseModel, Field 
from typing import Optional

# ---------------------------------
# Upload
# ---------------------------------

class UploadResponse(BaseModel):
    file_paths:list[str]
    file_names:list[str]
    count:int

# ---------------------------------
# Chat
# ---------------------------------

class ChatRequest(BaseModel):
    query:str=Field(..., min_length=1,max_length=10000)
    file_paths:list[str]=Field(default_factory=list)
    thread_id:Optional[str]=None

class ChatResponse(BaseModel):
    thread_id:str
    final_answer:str
    task:str

# ---------------------------------
# Stream events
# ---------------------------------

class StatusEvent(BaseModel):
    type:str="status"
    node:str
    message:str

class TokenEvent(BaseModel):
    type:str="token"
    content:str

class DoneEvent(BaseModel):
    type:str="done"
    thread_id:str
    task:str

class ErrorEvent(BaseModel):
    type:str="error"
    message:str


# ---------------------------------
# Reset
# ---------------------------------

class ResetRequest(BaseModel):
    thread_id:str

class ResetResponse(BaseModel):
    thread_id:str
    success:bool
    message:str