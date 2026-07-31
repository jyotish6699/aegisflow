from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models.event import Event
from models.session import Session
from api.events import router as events_router
from api.sessions import router as sessions_router

app = FastAPI()

app.include_router(events_router)
app.include_router(sessions_router)

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

