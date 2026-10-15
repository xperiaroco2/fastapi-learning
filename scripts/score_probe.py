import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from app.core.logger import logger, setup_logging

load_dotenv()
setup_logging()

embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"), query_encode_kwargs={"prompt": "query: "})

qdrant_url = os.getenv("VECTOR_DATABASE_URL")
collection_name = os.getenv("QDRANT_COLLECTION_NAME") or ""
vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings, url=qdrant_url, collection_name=collection_name
)

cases = [
    "Учень 7 класу постійно не виконує домашні завдання з математики і відволікається на уроках",
    "Дитина з особливими освітніми потребами не встигає за програмою, потрібна допомога асистента вчителя",
    "Учень систематично ображає та цькує однокласників, батьки скаржаться",
    "Учениця після переїзду погано володіє українською мовою і соромиться відповідати на уроках",
    "Як вчителю пройти підвищення кваліфікації і скільки годин на рік потрібно",
    "Рецепт борщу з пампушками та часником",
    "Як замінити масло в двигуні Toyota Corolla",
]

for query in cases:
    logger.info("similarity_search_start", query=query)
    for document, score in vector_store.similarity_search_with_score(query, 5, score_threshold=0.85):
        logger.info("similarity_search_result", document=document.page_content, score=score)
