"""
Phase 2 Ingestion Script:
Reads SOP documents from data/sops/, generates local embeddings
using Hugging Face SentenceTransformers (all-MiniLM-L6-v2, 384 dims),
and upserts them with metadata to a Pinecone Serverless Index.
"""
import os
import sys
import time
import glob

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pinecone import Pinecone, ServerlessSpec
from src.config.settings import settings
from src.rag.embeddings import get_text_embedding

def run_sops_ingestion():
    if not settings.PINECONE_API_KEY:
        print("[ERROR] PINECONE_API_KEY is not configured in your .env file.")
        return

    print("[INFO] Connecting to Pinecone...")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index_name = settings.PINECONE_INDEX_NAME

    # Ensure index exists with 384 dimensions for all-MiniLM-L6-v2
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"[INFO] Creating Pinecone serverless index '{index_name}' (dim=384, cosine)...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print("[INFO] Waiting for index to be ready...")
        while not pc.describe_index(index_name).status.get("ready"):
            time.sleep(2)
        print("[SUCCESS] Pinecone index is ready!")
    else:
        print(f"[INFO] Pinecone index '{index_name}' already exists.")

    index = pc.Index(index_name)

    sop_files = glob.glob(os.path.join("data", "sops", "*.md"))
    print(f"[INFO] Found {len(sop_files)} SOP documents in data/sops/.")

    records_to_upsert = []

    for file_path in sop_files:
        base_name = os.path.basename(file_path)
        print(f"  -> Processing: {base_name}")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Split markdown by sections (headers or double newlines)
        raw_sections = content.split("### ")
        for i, sec in enumerate(raw_sections):
            text = sec.strip()
            if not text or len(text) < 25:
                continue

            if not text.startswith("#"):
                text = "### " + text

            chunk_id = f"{os.path.splitext(base_name)[0]}-sec-{i}"
            vector = get_text_embedding(text)

            records_to_upsert.append({
                "id": chunk_id,
                "values": vector,
                "metadata": {
                    "text": text,
                    "source": base_name,
                    "chunk_id": chunk_id
                }
            })

    if records_to_upsert:
        print(f"[INFO] Upserting {len(records_to_upsert)} semantic chunks to Pinecone...")
        index.upsert(vectors=records_to_upsert)
        print("[SUCCESS] Phase 2 SOP Ingestion completed successfully!")

        # Wait a moment for indexing and print count
        time.sleep(2)
        stats = index.describe_index_stats()
        print(f"[VERIFIED] Total vectors in '{index_name}': {stats.get('total_vector_count')}")

if __name__ == "__main__":
    run_sops_ingestion()
