from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.services.gemini_service import GeminiService
from app.schemas import ExtractionResult
from app.utils.validation import validate_extraction

app = FastAPI(title="VLM Document Processing Pipeline")

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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
