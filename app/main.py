from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import check_db_connection, engine, setup_logging
from app.routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection()
    yield logger.info("Server started!")
    await engine.dispose()


logger = setup_logging()

app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint was called")
    return {"status": "ok"}
