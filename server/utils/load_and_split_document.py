from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from server.utils.log import logger


def load_and_split(file_path: str):
    logger.info(f"Starting PDF loading process for file: {file_path}")

    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        logger.info(f"Successfully loaded {len(documents)} documents from {file_path}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_documents = text_splitter.split_documents(documents=documents)
        logger.info(f"Successfully split documents into {len(split_documents)} chunks")

        return split_documents

    except Exception as e:
        logger.error(f"Error occurred while processing the file {file_path}: {str(e)}")
        return False
