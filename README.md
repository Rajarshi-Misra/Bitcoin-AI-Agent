# Bitcoin AI Agent

An intelligent Bitcoin assistant that provides real-time price information, answers questions about Bitcoin using the official whitepaper, and maintains conversation history. Built with FastAPI, PostgreSQL, and AI-powered RAG (Retrieval Augmented Generation).

## What It Does

- **Bitcoin Price Queries** - Get current Bitcoin prices in INR with caching
- **Knowledge Base Q&A** - Answer questions using Bitcoin whitepaper and documents
- **Multi-language Support** - Understands queries in any language, responds in English
- **Conversation History** - Maintains chat history for each user
- **User Management** - Secure authentication and user accounts

## How to Use

### 1. Setup
```bash
# Start database and Redis
docker-compose up -d

# Setup database schema
python -c "from bitcoin_agent.db.session import enable_pgvector; enable_pgvector()"
alembic upgrade head

# Load Bitcoin knowledge base
python knowledge_base/scripts/ingest_docs.py

# Start the API server
uvicorn bitcoin_agent.api.app:app --reload
```

### 2. Register and Login
```bash
# Register a new user
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "John Doe", "password": "password123"}'

# Login to get JWT token
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 3. Chat with the AI
```bash
# Ask about Bitcoin price
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current Bitcoin price?"}'

# Ask about Bitcoin concepts
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "How does Bitcoin mining work?"}'
```

### 4. Search Knowledge Base
```bash
# Search Bitcoin whitepaper
curl -X GET "http://localhost:8000/search?query=blockchain%20consensus&limit=3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Environment Variables

```env
TOGETHER_API_KEY=your_key
DATABASE_URL=postgresql://user:pass@localhost:5432/bitcoin_agent
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key
```

## Example Usage

### Price Queries
```
User: "What's the current Bitcoin price?"
AI: "The current Bitcoin price is ₹8,19,67,071 INR. This price is updated every 5 minutes with caching to ensure accuracy."

User: "Bitcoin कीमत क्या है?" (Hindi)
AI: "The current Bitcoin price is ₹8,19,67,071 INR. I understand you asked in Hindi, but I respond in English for consistency."
```

### Knowledge Base Queries
```
User: "How does Bitcoin mining work?"
AI: "Based on the Bitcoin whitepaper, mining works through a proof-of-work system where miners compete to solve cryptographic puzzles..."

User: "What is the purpose of the blockchain?"
AI: "According to the Bitcoin whitepaper, the blockchain serves as a public ledger that records all transactions in chronological order..."
```

## API Endpoints

- `POST /register` - Create new user account
- `POST /login` - Authenticate user and get JWT token
- `POST /chat` - Send message to AI (requires authentication)
- `GET /conversations` - Get user's conversation history
- `GET /search` - Search Bitcoin knowledge base
- `GET /docs` - Interactive API documentation at `http://localhost:8000/docs`

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector for vector search
- **AI Model**: LLaMA 3.1 8B via Together AI
- **Caching**: Redis
- **Authentication**: JWT tokens
- **Vector Search**: Sentence Transformers + pgvector
