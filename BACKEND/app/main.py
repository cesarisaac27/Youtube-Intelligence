from fastapi import FastAPI
from app.api.channels import router as channels_router
from app.api.videos import router as videos_router 
from fastapi.middleware.cors import CORSMiddleware


"""
python -m uvicorn main:app --reload
python -m uvicorn app.main:app --reload
http://127.0.0.1:8000/docs


Start FastApi app - YoutubeAnalytics 
"""
app = FastAPI(
    title="YouTube Analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(channels_router)
app.include_router(videos_router)