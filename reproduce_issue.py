import asyncio
import os
import fitz
from dotenv import load_dotenv
from app.services.gemini_service import GeminiService

load_dotenv()

async def reproduce():
    service = GeminiService()
    
    pdf_path = "/Users/bharani/Documents/Developer/quatrro/app/sampledoc/LoanPackage.pdf"
    
    print(f"Opening {pdf_path}...")
    doc = fitz.open(pdf_path)
    
    # Page 1 (index 0) and Page 22 (index 21) failed
    pages_to_test = [0, 21]
    
    for page_num in pages_to_test:
        print(f"\nProcessing page {page_num + 1}...")
        page = doc[page_num]
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        
        text_content = page.get_text()
        print(f"Page {page_num + 1} Text Content Preview (first 500 chars):")
        print(text_content[:500])
        print("-" * 20)
        
        try:
            # We call process_page_async directly
            result = await service.process_page_async(page_num + 1, img_data)
            
            if "error" in result:
                print(f"Page {page_num + 1} Failed: {result['error']}")
            else:
                print(f"Page {page_num + 1} Success!")
                print(f"Confidence: {result.get('confidence')}")
                # print(result)
            
        except Exception as e:
            print(f"Exception on page {page_num + 1}: {e}")

if __name__ == "__main__":
    asyncio.run(reproduce())
