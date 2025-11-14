from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

# Each Pydantic model corresponds to a MongoDB collection named after the class lowercased

class Contact(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=2000)

class Lead(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str
    source: str = "portfolio"

class VisitorEvent(BaseModel):
    type: str
    label: Optional[str] = None
    meta: Optional[dict] = None

class Project(BaseModel):
    title: str
    summary: str
    tech: List[str] = []
    highlight: Optional[str] = None
    links: Optional[dict] = None
