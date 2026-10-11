
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.database import Base, engine
from app.routes import router as accounts_router
from app.transaction_routes import router as transactions_router
from app.summary_routes import router as summary_router
from app.transfer_routes import router as transfers_router
from app.chat_routes.chat import router as chat_router
from app import models
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Expense Tracker API",
    description="API for managing personal expenses and bank accounts",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(summary_router)
app.include_router(transfers_router)
app.include_router(chat_router)


@app.get("/")
def home():
    return {"message": "Expense Tracker API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
