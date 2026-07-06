# AI Docs Chatbot 🤖

A RAG-based AI chatbot that lets you upload any PDF and chat with it using Claude AI.

## Live Demo
🔗 https://pavan-ai-docs-chatbot.streamlit.app/

## How it works
1. Upload a PDF document
2. The document is chunked, embedded and stored in Supabase (pgvector)
3. When you ask a question, relevant chunks are retrieved and sent to Claude API
4. Claude answers based only on your document content

## Tech Stack
- **Backend:** Python, FastAPI, Docker
- **Frontend:** Streamlit
- **Database:** Supabase (PostgreSQL + pgvector)
- **AI:** Anthropic Claude API, Sentence Transformers
- **Deployment:** Railway (backend), Streamlit Cloud (frontend)

## Run Locally

### Prerequisites
- Python 3.10+
- Docker
- Supabase account
- Anthropic API key

### Setup

1. Clone the repo:
```bash
git clone https://github.com/pavgreddy/ai-docs-chatbot.git
cd ai-docs-chatbot
```

2. Create `.env` in the `backend` folder:

ANTHROPIC_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_anon_key

3. Run the backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

4. Run the frontend:
```bash
cd frontend
pip install streamlit requests
streamlit run app.py
```

### Run with Docker
```bash
cd backend
docker build -t ai-docs-chatbot .
docker run -p 8000:8000 --env-file .env ai-docs-chatbot
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload-pdf` | Upload and index a PDF |
| POST | `/chat` | Ask a question about the document |