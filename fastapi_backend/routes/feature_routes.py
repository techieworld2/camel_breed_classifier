from fastapi import APIRouter, Depends, Query
from auth import get_current_user
from database import User
from gemini_service import get_gemini_service
from schemas import FactsResponse

router = APIRouter(prefix="/features", tags=["Features"])


@router.post("/facts", response_model=FactsResponse)
def get_breed_facts(
    breed_name: str = Query(..., description="Camel breed name"),
    current_user: User = Depends(get_current_user)
):
    """
    Get 10 facts about a camel breed using Gemini API
    """
    gemini = get_gemini_service()
    facts, error = gemini.get_10_facts(breed_name)
    
    return FactsResponse(
        breed=breed_name,
        facts=facts,
        error=error
    )
