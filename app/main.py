from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import links, auth
from app.database import Base, engine

app = FastAPI(
    title="URL Shortener API",
    description=(
        "Сервис для сокращения ссылок с аналитикой, "
        "авторизацией и кэшированием."
    ),
    version="1.0.0"
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="", tags=["Auth"])
app.include_router(links.router, prefix="", tags=["Links"])