from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import auth_routes, prediction_routes, feature_routes
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Camel Classifier API", version="1.0.0")

# CORS middleware - allow your Vercel frontend
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://*.vercel.app",   # Vercel preview deployments
    os.getenv("FRONTEND_URL", ""),  # Production frontend URL
]

# Remove empty strings
allowed_origins = [origin for origin in allowed_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/api")
app.include_router(prediction_routes.router, prefix="/api")
app.include_router(feature_routes.router, prefix="/api")


@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized")
    print("✅ ML model will be loaded on first prediction")
    print("🚀 Server running at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")


@app.get("/")
def root():
    return {
        "message": "Camel Classifier API",
        "docs": "/docs",
        "health": "OK"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
