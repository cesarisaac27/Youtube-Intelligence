from fastapi import FastAPI
from .api.channels import router as channels_router
from .api.videos import router as videos_router 
from fastapi.middleware.cors import CORSMiddleware


"""
python -m uvicorn main:app --reload
python -m uvicorn app.main:app --reload
http://127.0.0.1:8000/docs
retirados de env 
HOST=db.nxzprogsovnfpogcxhev.supabase.co
PORT=5432

Start FastApi app - YoutubeAnalytics 
"""
app = FastAPI(
    title="YouTube Intellligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_root():
    return {"msg": "API funcionando"}

app.include_router(channels_router)
app.include_router(videos_router)