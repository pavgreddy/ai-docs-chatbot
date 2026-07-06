from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client
import anthropic
import PyPDF2
import io
from sentence_transformers import SentenceTransformer

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(file_bytes):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    text = text.replace("\x00", "")
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def get_embedding(text):
    embedding = embedding_model.encode(text)
    return embedding.tolist()

@app.get("/")
def root():
    return {"message": "AI Docs Chatbot API is running!"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text)
    
    for chunk in chunks:
        embedding = get_embedding(chunk)
        supabase.table("documents").insert({
            "content": chunk,
            "embedding": embedding,
            "filename": file.filename
        }).execute()
    
    return {"message": f"Successfully uploaded and indexed {len(chunks)} chunks from {file.filename}"}

class ChatRequest(BaseModel):
    question: str
    filename: str

@app.post("/chat")
async def chat(request: ChatRequest):
    question_embedding = get_embedding(request.question)
    
    result = supabase.rpc("match_documents", {
        "query_embedding": question_embedding,
        "match_threshold": 0.0,
        "match_count": 5,
        "filter_filename": request.filename
    }).execute()
    
    context = "\n\n".join([doc["content"] for doc in result.data])
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Answer the question based on the context below. If the answer isn't in the context, say so.

Context:
{context}

Question: {request.question}"""
        }]
    )
    
    return {
        "answer": response.content[0].text,
        "sources": [doc["content"][:200] for doc in result.data]
    }