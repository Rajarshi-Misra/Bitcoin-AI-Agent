from sqlalchemy.orm import Session
from sqlalchemy import select, func
from bitcoin_agent.models.document import Document, DocumentChunk
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from typing import List

class VectorService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
    
    def generate_embedding(self, text: str):
        return self.model.encode(text).tolist()
    
    def add_document(self, db: Session, title: str, content: str, file_path: str, doc_type: str) -> Document:
        """Add document and its chunks to database"""
        # Create document
        doc = Document(title=title, content=content[:1000], file_path=file_path, doc_type=doc_type)
        db.add(doc)
        db.flush()  # Get doc.id
        
        # Split into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Add chunks with embeddings
        for idx, chunk_text in enumerate(chunks):
            embedding = self.generate_embedding(chunk_text)
            chunk = DocumentChunk(
                document_id=doc.id,
                content=chunk_text,
                chunk_index=idx,
                embedding=embedding
            )
            db.add(chunk)
        
        doc.chunk_count = len(chunks)
        db.commit()
        db.refresh(doc)
        return doc
    
    def search_similar(self, db: Session, query: str, limit: int = 3) -> List[DocumentChunk]:
        query_embedding = self.generate_embedding(query)
        
        stmt = (
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        chunks =  db.execute(stmt).scalars().all()
        return chunks
    
    def return_content(chunks):
        return "\n\n".join([chunk.content for chunk in chunks])
    
vector_service = VectorService()