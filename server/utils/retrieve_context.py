from server.utils.log import logger
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
import os

def retrieve_similar_docs(query, top_k=5, type: str = None):
    """Retrieves the most similar documents to the given query from Pinecone."""
    
    logger.info(f"Retrieving top {top_k} similar documents for query: {query}")

    try:
        api_key = os.getenv('OPENAI_API_KEY')
        pinecone_api_key = os.getenv('PINECONE_API_KEY')

        if not api_key or not pinecone_api_key:
            logger.error("API keys are missing in environment variables.")
            raise ValueError("Missing API keys.")

        embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-large"
        )

        pc = Pinecone(api_key=pinecone_api_key)
        index_name = "supportdocs"

        if index_name not in [index_info["name"] for index_info in pc.list_indexes()]:
            logger.error(f"Pinecone index '{index_name}' does not exist.")
            raise ValueError(f"Index '{index_name}' not found in Pinecone.")

        index = pc.Index(index_name)
        vector_store = PineconeVectorStore(index=index, embedding=embeddings, namespace=type)

        results = vector_store.similarity_search(query, k=top_k)

        if not results:
            logger.warning(f"No relevant documents found for query: {query}")
            return []
        
        logger.info(f"Found {len(results)} relevant documents for query.")

        return results

    except Exception as e:
        logger.error(f"Error occurred during document retrieval: {str(e)}")
        return False
    
def get_parsed_response(context):
    try:
        logger.info("Parsing response from context.")
        query_context = ""
        
        for doc_context in context:
            query_context += doc_context.page_content 
        
        logger.info("Parsing successful.")
        return query_context
    
    except Exception as e:
        logger.error(f"Error occurred while parsing response: {e}")
        return False