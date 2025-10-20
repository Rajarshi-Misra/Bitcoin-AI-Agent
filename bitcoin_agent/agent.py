from together import Together
from bitcoin_agent.config import settings
from bitcoin_agent.crypto import get_crypto_price
from bitcoin_agent.services.redis_service import redis_service
from bitcoin_agent.services.vector_service import vector_service
from bitcoin_agent.services.conversation_service import add_message
from bitcoin_agent.models.message import MessageRole
from sqlalchemy.orm import Session

client = Together(api_key=settings.TOGETHER_API_KEY)

crypto_price_tool = [{
    "type": "function",
    "function": {
        "name": "get_crypto_price",
        "description": "Get current price of bitcoin in INR"
    }
}]

def build_system_prompt(context: str = "") -> str:
    base_prompt = """You are a helpful Bitcoin AI assistant with access to:
        1. Real-time Bitcoin prices
        2. Bitcoin knowledge base
        Provide accurate, helpful information about Bitcoin."""
    if context:
        base_prompt += f"\n"
    return base_prompt

def process_user_input(user_input: str, db: Session, conversation_id: int, use_rag: bool = True) -> str:
    """Process user input with database persistence and RAG"""
    
    add_message(db, conversation_id, MessageRole.USER, user_input)
    
    rag_context = ""
    if use_rag and any(kw in user_input.lower() for kw in ["bitcoin", "btc", "whitepaper", "blockchain"]):
        rag_context = vector_service.search_similar(db, user_input)

    messages = [
        {"role": "system", "content": build_system_prompt(rag_context)},
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.7,
        tools=crypto_price_tool
    )
    
    if response.choices[0].message.tool_calls:
        price = redis_service.get("price:bitcoin")
        if not price:
            price = get_crypto_price()
            print(price)
            redis_service.set("price:bitcoin", price, expire_seconds=300)
        
        messages.append({
            "tool_call_id": response.choices[0].message.tool_calls[0].id,
            "role": "tool",
            "name": "get_crypto_price",
            "content": f"Current Bitcoin price in INR: {price}"
        })
        
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
    
    assistant_response = response.choices[0].message.content
    
    # Save assistant message
    add_message(db, conversation_id, MessageRole.ASSISTANT, assistant_response)
    
    return assistant_response