from pathlib import Path
from bitcoin_agent.services.vector_service import vector_service
from bitcoin_agent.db.session import SessionLocal

def read_file(file_path: Path):
    return file_path.read_text(encoding='utf-8')

def ingest_documents(docs_dir: str = "./knowledge_base/bitcoin_docs"):
    docs_path = Path(docs_dir)
    db = SessionLocal()
    
    for file_path in docs_path.glob("*"):
        if file_path.suffix not in ['.txt']:
            continue
        
        print(f"Processing {file_path.name}...")
        content = read_file(file_path)
        
        doc = vector_service.add_document(
            db=db,
            title=file_path.name,
            content=content,
            file_path=str(file_path),
            doc_type=file_path.suffix[1:]
        )
        
        print(f"✓ Ingested {doc.chunk_count} chunks from {file_path.name}")
    
    db.close()

if __name__ == "__main__":
    ingest_documents()