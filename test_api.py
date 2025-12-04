from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.endpoints.games import get_march1_ohio_games

app = FastAPI(
    title="Soccer Streak Analyzer API",
    description="Ohio-legal soccer betting analysis API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Soccer Streak Analyzer API", "status": "running"}

@app.get("/api/v1/games/march1")
def march1_endpoint():
    """Call the games endpoint function"""
    return get_march1_ohio_games()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)