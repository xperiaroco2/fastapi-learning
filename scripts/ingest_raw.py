import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import cast
from uuid import uuid5

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import MarkdownTextSplitter
from llama_cloud import AsyncLlamaCloud
from llama_cloud.types.parsing_get_response import MarkdownPageMarkdownResultPage

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
    async with semaphore:
        try:
            logger.info("ingest_file_started", file=filename)

            client = AsyncLlamaCloud(
                api_key=os.environ.get("LLAMA_CLOUD_API_KEY"),
            )

            file_response = await client.files.create(
                file=Path(path),
                purpose="parse",
            )

            result = await client.parsing.parse(
                tier="cost_effective", version="latest", file_id=file_response.id, expand=["markdown"]
            )

            assert result.markdown is not None

            full_text = "\n\n".join(
                [cast(MarkdownPageMarkdownResultPage, page).markdown for page in result.markdown.pages]
            )
            base_metadata = {
                "source_file": filename,
                "ingested_at": datetime.now().isoformat(),
                "category": "education",
            }

            logger.info("ingest_file_chunking_started", file=filename)

            splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)

            chunks = splitter.create_documents([full_text], metadatas=[base_metadata])

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
    tasks = [parse_pdf(f"data/samples/{pdf_path}", filename=pdf_path) for pdf_path in os.listdir("data/samples")]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(parse_all_pdfs_in_dir())
