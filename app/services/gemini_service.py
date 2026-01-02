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

class GeminiService:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        # Semaphore to limit concurrent requests (e.g., 5-10) to avoid rate limits
        self.semaphore = asyncio.Semaphore(5)
        self.logger = logging.getLogger(__name__)

    async def process_page_async(self, page_num: int, img_data: bytes) -> Dict[str, Any]:
        async with self.semaphore:
            prompt = f"""
            Classify this mortgage document page (page {page_num}) and extract fields as JSON.
            
            Strictly classify the document into one of the following specific types (return the specific type name, e.g., "Fannie1004", "Form1040"):

            Tax: Form1040, Form1065, Form1120S, W2, 1099-MISC, ScheduleC, K1
            Appraisal: Fannie1004, Freddie70, Desktop, DriveBy, URAR
            Credit: TriMerge, MergedInFile, Equifax, TransUnion, Experian
            Income: Paystub, PensionVerification, ProfitLoss, BankStatement
            Title/Escrow: ALTA_Commitment, Preliminary_Title, HUD1, ClosingDisclosure
            Loan: MortgageStatement, Note, BorrowerAuthorization
            Govt/Military: VA_Certificate, DD214, COE
            Misc: Continuation, CoverLetter, Illegible, Blank

            Output format (JSON only):
            {{
              "doc_type": "SpecificTypeFromListAbove",
              "confidence": 0.95,
              "fields": {{ ... }}
            }}
            
            IMPORTANT: Extract ONLY the values. Do not reproduce the standard form text or legal disclaimers.
            """
            
            try:
                # Use generate_content_async
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
                # With JSON mode, response.text should be valid JSON directly
                return json.loads(text)
            except Exception as e:
                # Fallback for parsing if needed or handle other errors
                if "finish_reason" in str(e) and "5" in str(e):
                    # Recitation Error: Try fallback to just classify doc_type without extraction
                    self.logger.warning(f"Recitation error on page {page_num}. Retrying with classification only.")
                    try:
                        fallback_prompt = """
                        Classify this document image into one of the following types:
                        Tax: Form1040, Form1065, Form1120S, W2, 1099-MISC, ScheduleC, K1
                        Appraisal: Fannie1004, Freddie70, Desktop, DriveBy, URAR
                        Credit: TriMerge, MergedInFile, Equifax, TransUnion, Experian
                        Income: Paystub, PensionVerification, ProfitLoss, BankStatement
                        Title/Escrow: ALTA_Commitment, Preliminary_Title, HUD1, ClosingDisclosure
                        Loan: MortgageStatement, Note, BorrowerAuthorization
                        Govt/Military: VA_Certificate, DD214, COE
                        Misc: Continuation, CoverLetter, Illegible, Blank

                        Output format (JSON only):
                        {
                          "doc_type": "SpecificTypeFromListAbove",
                          "fields": {}
                        }
                        Do not extract any text content.
                        """
                        response = await self.model.generate_content_async(
                            [fallback_prompt, {"mime_type": "image/png", "data": img_data}],
                            safety_settings=safety_settings,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        return json.loads(response.text)
                    except Exception as fallback_e:
                         return {"error": f"Recitation Error (Blocked) and Fallback Failed: {str(fallback_e)}"}
                
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
                    fields=result.get("fields", {})
                ))

        return ExtractionResult(
            doc_type="Mixed", 
            confidence=0.9, 
            pages=pages_data,
            validation=validation_warnings
        )
