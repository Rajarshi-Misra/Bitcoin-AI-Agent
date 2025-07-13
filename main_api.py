from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from main import process_user_input
from crypto import get_crypto_price
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    response = process_user_input(request.message)
    return {"response": response}

@app.get("/price")
def price():
    price_inr = get_crypto_price()
    return {"price_inr": price_inr}

