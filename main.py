from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

from app.services.gemini_service import GeminiService
from app.schemas import ExtractionResult
from app.utils.validation import validate_extraction
from app.logging_config import setup_logging

# Setup Logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="VLM Document Processing Pipeline")

# Middleware for request logging
class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        url = request.url.path
        
        logger.info(f"Request started: {method} {url}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"Request finished: {method} {url} status={response.status_code} duration={process_time:.4f}s")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {method} {url} duration={process_time:.4f}s error={str(e)}")
            raise e

app.add_middleware(LogRequestsMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

gemini_service = GeminiService()

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.post("/process", response_model=ExtractionResult)
async def process_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    
    try:
        result = await gemini_service.process_document_async(content, file.filename)
        
        # Run validation
        validation_result = validate_extraction(result.model_dump())
        result.validation.extend(validation_result)
        
        return result
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
