from fastapi import FastAPI
from app.api.intent_routes import router as intent_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Aegisflow API",
        version="1.0.0"
    )

    # Register routes
    app.include_router(intent_router, prefix="/api")
    return app

app = create_app()

# Lifecycle hooks (optional but important later)
@app.on_event("startup")
def on_startup():
    print("Aegisflow system booted")

@app.on_event("shutdown")
def on_shutdown():
    print("Aegisflow system stopped")
    