from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionRequest(BaseModel):
    head_size: float = Field(3.0, ge=0.0, le=5.0)
    leg_condition: float = Field(3.0, ge=0.0, le=5.0)
    coat_quality: float = Field(3.0, ge=0.0, le=5.0)
    overall_fitness: float = Field(3.0, ge=0.0, le=5.0)
    confidence_threshold: float = Field(0.60, ge=0.0, le=1.0)


class PredictionResponse(BaseModel):
    id: int
    breed: str
    confidence: float
    rating: float
    probabilities: Dict[str, float]
    gradcam_image: str
    is_dromedary_fallback: bool
    head_size: float
    leg_condition: float
    coat_quality: float
    overall_fitness: float
    created_at: datetime

    class Config:
        from_attributes = True


class FactsResponse(BaseModel):
    breed: str
    facts: list[str]
    error: Optional[str] = None
