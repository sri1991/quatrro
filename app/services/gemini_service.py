import os
import fitz  # PyMuPDF
import json
import asyncio
import time
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv()
from app.schemas import ExtractionResult, PageData
from app.services.training_service import TrainingService

class GeminiService:
    def __init__(self, training_service: TrainingService = None):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        # Semaphore to limit concurrent requests (e.g., 5-10) to avoid rate limits
        self.semaphore = asyncio.Semaphore(5)
        # Using root logger or specific logger module
        self.logger = logging.getLogger(__name__)
        
        # Inject or instantiate TrainingService
        self.training_service = training_service or TrainingService()

    def _build_classification_prompt(self, page_num: int) -> str:
        """Constructs the classification and extraction prompt dynamically from config."""
        
        configs = self.training_service.get_all_configs()
        
        # Build the dynamic parts of the prompt
        classification_rules = []
        extraction_schemas = []

        for config in configs:
            doc_type = config.get("doc_type")
            keywords = ", ".join(config.get("keywords", []))
            anti_keywords = ", ".join(config.get("anti_keywords", []))
            fields_schema = json.dumps(config.get("fields", {}), indent=2)

            classification_rules.append(
                f"- **{doc_type}**: Look for keywords: [{keywords}]."
            )
            
            extraction_schemas.append(
                f"### {doc_type} Schema\n{fields_schema}"
            )
            
        rules_text = "\n".join(classification_rules)
        schemas_text = "\n\n".join(extraction_schemas)
        
        prompt = f"""
        Analyze this document page (page {page_num}) and extract structured data.
        
        ### Classification Rules
        Determine the document type based on the following rules:
        {rules_text}
        - **Other**: If the document does not match any of the above strict criteria.
        
        ### Extraction Rules
        If the document matches one of the types above, extract the fields EXACTLY as defined in the following schemas. 
        Do not look for fields that are not in the schema.
        
        {schemas_text}
        
        Output valid JSON only:
        {{
          "doc_type": "TheMatchedDocType",
          "confidence": 0.95,
          "fields": {{
             // Extract fields exactly matching the schema for the doc_type.
             // Nested objects should be preserved.
          }}
        }}
        """
        return prompt

    async def process_page_async(self, page_num: int, img_data: bytes) -> Dict[str, Any]:
        async with self.semaphore:
            prompt = self._build_classification_prompt(page_num)
            
            try:
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
                
                response = await self.model.generate_content_async(
                    [prompt, {"mime_type": "image/png", "data": img_data}],
                    safety_settings=safety_settings,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                text = response.text
                return json.loads(text)
            except Exception as e:
                self.logger.error(f"Error processing page {page_num}: {e}")
                return {"error": str(e)}

    async def process_document_async(self, file_content: bytes, filename: str = "document.pdf") -> ExtractionResult:
        start_time = time.time()
        self.logger.info(f"Starting processing for {filename}")
        
        doc = fitz.open(stream=file_content, filetype="pdf")
        total_pages = len(doc)
        self.logger.info(f"Document has {total_pages} pages. Processing in parallel...")
        
        tasks = []
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            tasks.append(self.process_page_async(page_num + 1, img_data))
        
        # Run all page processing in parallel
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        self.logger.info(f"Finished processing {filename} in {duration:.2f} seconds. Pages: {total_pages}")
        
        pages_data = []
        validation_warnings = []
        
        for i, result in enumerate(results):
            page_num = i + 1
            if "error" in result:
                validation_warnings.append(f"Page {page_num}: {result['error']}")
            else:
                pages_data.append(PageData(
                    page_num=page_num,
                    doc_type=result.get("doc_type", "Unknown"),
                    confidence=result.get("confidence", 0.0),
                    fields=result.get("fields", {})
                ))

        # Calculate average confidence
        if pages_data:
            total_confidence = sum(p.confidence for p in pages_data)
            avg_confidence = total_confidence / len(pages_data)
            avg_confidence = round(avg_confidence, 2)
        else:
            avg_confidence = 0.0

        return ExtractionResult(
            doc_type="Mixed", 
            confidence=avg_confidence, 
            pages=pages_data,
            validation=validation_warnings
        )
