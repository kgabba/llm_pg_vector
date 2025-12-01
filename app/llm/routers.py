from fastapi import APIRouter, Depends
from models.model import TextIn
from db.utils import conn_to_db
from llm.deps import chunk_and_embed_to_db

router_llm = APIRouter(prefix='/llm')

@router_llm.post("/embed")
def create_embeddings(payload: TextIn, conn = Depends(conn_to_db)):
    inserted = chunk_and_embed_to_db(payload.text, conn)
    return {"status": "ok", "chunks_added_counts": inserted}