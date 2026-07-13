from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models.event import Event
from api.events import router

app = FastAPI()

app.include_router(router)

# Create database tables
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

