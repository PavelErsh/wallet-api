from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wallet API", version="1.0.0")


@app.post(
    "/api/v1/wallets/{wallet_id}/operation", response_model=schemas.OperationResponse
)
def perform_wallet_operation(
    wallet_id: str, operation: schemas.OperationBase, db: Session = Depends(get_db)
):
    transaction, error = crud.perform_operation(db, wallet_id, operation)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return transaction


@app.get("/api/v1/wallets/{wallet_id}", response_model=schemas.WalletResponse)
def get_wallet_balance(wallet_id: str, db: Session = Depends(get_db)):
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@app.post("/api/v1/wallets/", response_model=schemas.WalletResponse)
def create_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
    db_wallet, error = crud.create_wallet(db, wallet)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_wallet


@app.get("/")
def read_root():
    return {"message": "Wallet API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
