import os
import time
from langchain_openai import OpenAIEmbeddings
from server.utils.log import logger
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import os
from langchain_pinecone import PineconeVectorStore

load_dotenv()

def create_and_store_embeddings(docs, type: str):
    logger.info("Starting embedding creation process.")

    try:
        if not docs:
            logger.warning("No documents provided for embedding.")
            return []
        
        api_key = os.getenv('OPENAI_API_KEY')
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        
        if not api_key:
            logger.error("OPENAI_API_KEY is not set in environment variables.")
            raise ValueError("Missing OpenAI API key.")
        if not pinecone_api_key:
            logger.error("PINECONE_API_KEY is not set in environment variables.")
            raise ValueError("Missing Pinecone API key.")
        
        logger.info("Initializing Pinecone and OpenAI embedding model.")
        
        pc = Pinecone(api_key=pinecone_api_key)
        embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-large"
        )

        index_name = "supportdocs"

        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        logger.info(f"Existing Pinecone indexes: {existing_indexes}")

        if index_name not in existing_indexes:
            logger.info(f"Creating new Pinecone index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        
        index = pc.Index(index_name)
        logger.info(f"Connected to Pinecone index: {index_name}")

        vector_store = PineconeVectorStore(index=index, embedding=embeddings, namespace=type)
        logger.info("Initialized Pinecone vector store.")

        logger.info("Waiting for Pinecone index to become ready...")
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)
        
        logger.info("Pinecone index is ready. Adding documents...")
        vector_store.add_documents(documents=docs)
        logger.info(f"Successfully added {len(docs)} documents to Pinecone.")
        
        return True

    except Exception as e:
        logger.error(f"Error occurred during embedding creation: {str(e)}")
        return False
