from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import categories, bills, ocr, items

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bill Tracker API",
    description="API for tracking bills and expenses with OCR support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(categories.router)
app.include_router(bills.router)
app.include_router(ocr.router)
app.include_router(items.router)


@app.get("/")
def root():
    return {
        "message": "Bill Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
