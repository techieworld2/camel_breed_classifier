from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db, User, Prediction
from auth import get_current_user
from ml_model import get_classifier
from schemas import PredictionResponse
import json

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/classify", response_model=PredictionResponse)
async def classify_camel(
    file: UploadFile = File(...),
    head_size: float = Form(3.0),
    leg_condition: float = Form(3.0),
    coat_quality: float = Form(3.0),
    overall_fitness: float = Form(3.0),
    confidence_threshold: float = Form(0.60),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Classify camel breed from image with tabular features
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Get classifier and make prediction
    classifier = get_classifier()
    result = classifier.predict(
        image_bytes=image_bytes,
        head_size=head_size,
        leg_condition=leg_condition,
        coat_quality=coat_quality,
        overall_fitness=overall_fitness,
        conf_thresh=confidence_threshold
    )
    
    # Save prediction to database
    prediction = Prediction(
        user_id=current_user.id,
        breed=result["breed"],
        confidence=result["confidence"],
        rating=result["rating"],
        head_size=head_size,
        leg_condition=leg_condition,
        coat_quality=coat_quality,
        overall_fitness=overall_fitness,
        gradcam_image=result["gradcam_image"],
        probabilities=json.dumps(result["probabilities"])
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    # Return response
    return PredictionResponse(
        id=prediction.id,
        breed=prediction.breed,
        confidence=prediction.confidence,
        rating=prediction.rating,
        probabilities=result["probabilities"],
        gradcam_image=prediction.gradcam_image,
        is_dromedary_fallback=result["is_dromedary_fallback"],
        head_size=prediction.head_size,
        leg_condition=prediction.leg_condition,
        coat_quality=prediction.coat_quality,
        overall_fitness=prediction.overall_fitness,
        created_at=prediction.created_at
    )


@router.get("/history")
def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Get user's prediction history"""
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "breed": p.breed,
            "confidence": p.confidence,
            "rating": p.rating,
            "probabilities": json.loads(p.probabilities),
            "created_at": p.created_at
        }
        for p in predictions
    ]


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific prediction by ID"""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return PredictionResponse(
        id=prediction.id,
        breed=prediction.breed,
        confidence=prediction.confidence,
        rating=prediction.rating,
        probabilities=json.loads(prediction.probabilities),
        gradcam_image=prediction.gradcam_image,
        is_dromedary_fallback=prediction.breed == "Arabian Camel (Dromedary)",
        head_size=prediction.head_size,
        leg_condition=prediction.leg_condition,
        coat_quality=prediction.coat_quality,
        overall_fitness=prediction.overall_fitness,
        created_at=prediction.created_at
    )


@router.delete("/{prediction_id}")
def delete_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a prediction"""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    db.delete(prediction)
    db.commit()
    return {"message": "Prediction deleted successfully"}
