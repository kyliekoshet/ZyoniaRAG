from fastapi import FastAPI
from api import router

# Initialize FastAPI app
app = FastAPI(title="Vector Store API")

# Include API routes
app.include_router(router)

# For development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 