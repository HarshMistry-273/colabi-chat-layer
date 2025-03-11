from fastapi import APIRouter, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from server.utils.log import logger
from server.utils.load_and_split_document import load_and_split
from server.utils.generate_and_store_embeddings import create_and_store_embeddings

from dotenv import load_dotenv
import os

load_dotenv()

upload_router = APIRouter()

@upload_router.post('/files/upload')
def upload_file_processing(file: UploadFile, type: str):
    try:
        logger.info(f"Received file: {file.filename}")
        if not os.path.exists(os.getenv('STATIC_DIR')):
            os.makedirs(os.getenv('STATIC_DIR'))
            logger.info(f"Static Directory created: {os.getenv('STATIC_DIR')}")
            
        file_path = rf"{os.getenv('STATIC_DIR')}/{file.filename}"
        
        with open(file_path, "+wb") as f:
            f.write(file.file.read())
            logger.info(f"File saved at: {file_path}")
        
        logger.info(f"Processing file: {file.filename}")
        docs = load_and_split(file_path=file_path)
        if not docs:
            logger.error(f"Failed to process file: {file.filename}")
        logger.info(f"Processed file: {file.filename}")
        
        logger.info(f"Generating embeddings for: {file.filename}")
        if not create_and_store_embeddings(docs=docs, type=type):
            logger.error(f"Failed to generate embeddings for: {file.filename}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create or store embeddngs in vector store.")
        
        logger.info("File processed and sending response")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=
            {
                "data": "File uploaded and embeddings created.",
                "error": None,
                "status": True
            })

    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content=
            {
                "data": e.detail,
                "error": "",
                "status": False
            })
    
    except Exception as e:
        logger.error(f"An error occured during file processing: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=
            {
                "data": "An error occured",
                "error": str(e),
                "status": False
            }
        )