
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.database import Base, engine
from app.routes import router as accounts_router
from app.transaction_routes import router as transactions_router
from app.summary_routes import router as summary_router
from app.transfer_routes import router as transfers_router
from app import models


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

app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(summary_router)
app.include_router(transfers_router)


@app.get("/")
def home():
    return {"message": "Expense Tracker API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
