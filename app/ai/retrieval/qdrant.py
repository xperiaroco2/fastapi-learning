from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.ai.retrieval.abc import AIRetrieval
from app.core.config import get_settings
from app.core.logger import logger

collection_name = get_settings().qdrant_collection_name
embeddings: HuggingFaceEmbeddings
client: QdrantClient
db: QdrantVectorStore | None = None


def init_db():
    global embeddings
    global client
    global db

    embeddings = HuggingFaceEmbeddings(
        model_name=get_settings().embedding_model, query_encode_kwargs={"prompt": "query: "}
    )
    client = QdrantClient(url=get_settings().vector_database_url)
    db = QdrantVectorStore(client=client, collection_name=collection_name, embedding=embeddings)


class QdrantAIRetrieval(AIRetrieval):
    async def search(self, query: str) -> list[str]:
        try:
            if not db:
                init_db()

            assert db is not None

            result = await db.asimilarity_search(query, 5, score_threshold=get_settings().retrieval_score_threshold)
        except Exception:
            logger.exception("retrieval_failed")
            return []

        return [doc.page_content for doc in result]
