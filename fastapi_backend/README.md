# Camel Classifier - FastAPI Backend Setup Guide

## 🎯 Overview

Your Streamlit camel classifier has been converted to a **FastAPI backend** with **authentication** and all the original functionality:
- ✅ Image + Tabular Features Classification (Head Size, Leg Condition, Coat Quality, Overall Fitness)
- ✅ Grad-CAM Visualization
- ✅ Gemini AI Fact Generation (10 facts per breed)
- ✅ User Authentication (Signup/Login with JWT)
- ✅ Prediction History Storage

## 📁 Backend Structure

```
fastapi_backend/
├── main.py                 # FastAPI application entry point
├── database.py             # SQLAlchemy models (User, Prediction)
├── auth.py                 # JWT authentication
├── schemas.py              # Pydantic request/response models
├── ml_model.py             # ImageTabularNet + Grad-CAM
├── gemini_service.py       # Gemini AI integration
├── requirements.txt        # Python dependencies
├── best_model.pt           # Your trained model
└── routes/
    ├── __init__.py
    ├── auth_routes.py      # /api/auth/* endpoints
    ├── prediction_routes.py # /api/predict/* endpoints
    └── feature_routes.py   # /api/features/* endpoints
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd fastapi_backend

# Install in your camel_fyp environment
conda activate camel_fyp
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in `fastapi_backend/`:

```env
SECRET_KEY=your-secret-key-change-this-in-production-make-it-long-and-random
GEMINI_API_KEY=your-gemini-api-key-here
```

Or export them:

```bash
export SECRET_KEY="your-secret-key"
export GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Run the Server

```bash
python main.py
```

Server will start at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs** (Interactive Swagger UI)

## 📡 API Endpoints

### Authentication Endpoints

#### 1. Signup
```http
POST /api/auth/signup
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "bearer"
}
```

#### 2. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "bearer"
}
```

#### 3. Get Current User
```http
GET /api/auth/me
Authorization: Bearer <your_token>

Response:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-10-29T20:00:00"
}
```

### Prediction Endpoints

#### 4. Classify Camel (with Tabular Features!)
```http
POST /api/predict/classify
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

Form Data:
- file: <image file>
- head_size: 3.5 (0.0-5.0)
- leg_condition: 4.0 (0.0-5.0)
- coat_quality: 3.8 (0.0-5.0)
- overall_fitness: 4.2 (0.0-5.0)
- confidence_threshold: 0.60 (0.0-1.0)

Response:
{
  "id": 1,
  "breed": "Majaheem Camel",
  "confidence": 0.92,
  "rating": 4.15,
  "probabilities": {
    "Majaheem Camel": 0.92,
    "Bactrian Camel": 0.05,
    "Libyan Camel": 0.03
  },
  "gradcam_image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "is_dromedary_fallback": false,
  "head_size": 3.5,
  "leg_condition": 4.0,
  "coat_quality": 3.8,
  "overall_fitness": 4.2,
  "created_at": "2025-10-29T20:30:00"
}
```

#### 5. Get Prediction History
```http
GET /api/predict/history?skip=0&limit=10
Authorization: Bearer <your_token>

Response:
[
  {
    "id": 2,
    "breed": "Bactrian Camel",
    "confidence": 0.87,
    "rating": 3.95,
    "probabilities": {...},
    "created_at": "2025-10-29T20:30:00"
  },
  ...
]
```

#### 6. Get Specific Prediction
```http
GET /api/predict/1
Authorization: Bearer <your_token>
```

#### 7. Delete Prediction
```http
DELETE /api/predict/1
Authorization: Bearer <your_token>
```

### Feature Endpoints

#### 8. Get Breed Facts (Gemini AI)
```http
POST /api/features/facts?breed_name=Majaheem%20Camel
Authorization: Bearer <your_token>

Response:
{
  "breed": "Majaheem Camel",
  "facts": [
    "Majaheem camels are native to Saudi Arabia and highly valued for racing.",
    "They can reach speeds of up to 65 km/h in short bursts.",
    "The breed is known for its slender build and long legs.",
    "Majaheem camels have excellent endurance in desert conditions.",
    "They are primarily single-humped dromedaries with distinctive features.",
    "The breed has been selectively bred for centuries for racing performance.",
    "Majaheem camels are considered one of the most expensive camel breeds.",
    "They have a lighter coat color compared to other Arabian camels.",
    "The breed exhibits superior heat tolerance and water conservation.",
    "Majaheem camels are culturally significant in Gulf Arab heritage."
  ],
  "error": null
}
```

## 🧪 Testing with cURL

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

### Classify (save token from login first)
```bash
TOKEN="your_token_here"

curl -X POST http://localhost:8000/api/predict/classify \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/camel.jpg" \
  -F "head_size=3.5" \
  -F "leg_condition=4.0" \
  -F "coat_quality=3.8" \
  -F "overall_fitness=4.2" \
  -F "confidence_threshold=0.60"
```

### Get Facts
```bash
curl -X POST "http://localhost:8000/api/features/facts?breed_name=Majaheem%20Camel" \
  -H "Authorization: Bearer $TOKEN"
```

## 🧩 Key Features Preserved from Streamlit

### 1. **Tabular Features** ✅
The 4 sliders from your Streamlit app are now API parameters:
- `head_size` (0.0-5.0)
- `leg_condition` (0.0-5.0)
- `coat_quality` (0.0-5.0)
- `overall_fitness` (0.0-5.0)

These feed into your `ImageTabularNet` model exactly like before.

### 2. **Grad-CAM Visualization** ✅
- Generated automatically for every prediction
- Returned as base64-encoded PNG
- Uses the same `_ActGradHook` class from your Streamlit app

### 3. **Confidence Threshold** ✅
- Default: 0.60
- If confidence < threshold → "Arabian Camel (Dromedary)" fallback
- Exactly like your original logic

### 4. **Gemini AI Facts** ✅
- Same 3-strategy approach (JSON → Bullets → Plain)
- Returns exactly 10 facts
- Supports gemini-2.0-flash-exp model

### 5. **Breed Probabilities** ✅
- Returns probabilities for all 3 breeds
- Perfect for bar charts in frontend

## 🎨 Next Steps: Frontend

You can build a frontend with:
1. **React/Next.js** - Modern UI with components
2. **Recharts** - For probability bar charts
3. **React-Toastify** - For notifications

Or continue using the existing frontend we created earlier.

## 🐛 Troubleshooting

### Model Not Found
```bash
# Copy your model to backend folder
cp app/best_model.pt fastapi_backend/best_model.pt
```

### Gemini API Not Working
- Check `GEMINI_API_KEY` is set
- Install: `pip install google-genai`

### Database Issues
```bash
# Delete and recreate database
rm camel_classifier.db
# Restart server (it will auto-create tables)
python main.py
```

## 📊 Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `hashed_password`
- `created_at`

### Predictions Table
- `id` (Primary Key)
- `user_id` (Foreign Key → Users)
- `breed`
- `confidence`
- `rating`
- `head_size`, `leg_condition`, `coat_quality`, `overall_fitness`
- `gradcam_image` (Base64)
- `probabilities` (JSON)
- `created_at`

## 🔒 Security Notes

1. **Change SECRET_KEY** in production
2. Use **HTTPS** for production deployment
3. Add **rate limiting** if needed
4. Store **GEMINI_API_KEY** securely

## 🚢 Deployment

For production:
1. Use proper SECRET_KEY (generate with `openssl rand -hex 32`)
2. Use PostgreSQL instead of SQLite
3. Add Gunicorn/Uvicorn workers
4. Deploy on AWS/GCP/Azure with Docker

---

Your camel classifier is now a professional API! 🐪✨
