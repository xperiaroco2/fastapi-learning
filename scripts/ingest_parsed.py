import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from uuid import uuid5

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import MarkdownTextSplitter

from app.core.logger import logger, setup_logging

load_dotenv()
setup_logging()

logger.info("ingest_file_init", "Loading local embeddings...")

embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"), encode_kwargs={"prompt": "passage: "})

qdrant_url = os.getenv("VECTOR_DATABASE_URL")
collection_name = os.getenv("QDRANT_COLLECTION_NAME")
vector_store = QdrantVectorStore.from_documents([], embeddings, url=qdrant_url, collection_name=collection_name)

CONCURRENCY_LIMIT = 5
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)


async def parse_pdf(path: str, filename: str):
    if not path.endswith(".md"):
        return

    async with semaphore:
        try:
            logger.info("ingest_file_started", file=filename)

            base_metadata = {
                "source_file": filename,
                "ingested_at": datetime.now().isoformat(),
                "category": "education",
            }

            logger.info("ingest_file_chunking_started", file=filename)

            text = Path(path).read_text(encoding="utf-8")

            splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)

            chunks = splitter.create_documents([text], metadatas=[base_metadata])

            logger.info("ingest_file_chunking_finished", file=filename, chunks=len(chunks))

            ids = []

            for idx, chunk in enumerate(chunks):
                chunk.metadata["chunk_id"] = idx
                ids.append(uuid5(uuid.NAMESPACE_URL, f"{filename}:{idx}"))

            logger.info("ingest_file_storing", file=filename)

            await vector_store.aadd_documents(chunks, ids=ids)

            logger.info("ingest_file_success", file=filename)
        except Exception:
            logger.exception("ingest_file_error", file=filename)


async def parse_all_pdfs_in_dir():
    tasks = [
        parse_pdf(f"data/parsed/{file['source_file'].replace('.pdf', '.md')}", filename=file["source_file"])
        for file in json.loads(Path("data/parsed/_manifest.json").read_text())
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(parse_all_pdfs_in_dir())
