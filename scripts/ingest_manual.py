import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import MarkdownTextSplitter
from llama_cloud import AsyncLlamaCloud
from llama_cloud.types.parsing_get_response import MarkdownPageMarkdownResultPage

load_dotenv()

print("Loading local embeddings...")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

qdrant_url = os.getenv("VECTOR_DATABASE_URL")
collection_name = "my_knowledge"

vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings, collection_name=collection_name, url=qdrant_url
)

CONCURRENCY_LIMIT = 5
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)


async def parse_pdf(path: str, filename: str):
    async with semaphore:
        try:
            print(f"[{filename}]: Sending to LlamaParse...")

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

            print(f"[{filename}]: Making chunks...")

            splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)

            chunks = splitter.create_documents([full_text], metadatas=[base_metadata])

            print(f"[{filename}]: Made {len(chunks)} chunks.")

            for idx, chunk in enumerate(chunks):
                chunk.metadata["chunk_id"] = idx

            print(f"[{filename}]: Sending to Qdrant...")

            await vector_store.aadd_documents(chunks)

            print(f"[{filename}]: Success!")
        except Exception:
            print(f"[{filename}]: Error while processing file")


async def parse_all_pdfs_in_dir():
    tasks = [parse_pdf(f"data/samples/{pdf_path}", pdf_path) for pdf_path in os.listdir("data/samples/")]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(parse_all_pdfs_in_dir())
