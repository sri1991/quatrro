import asyncio
import sys
import os
import logging

# Add current directory to path so we can import 'app'
sys.path.append(os.getcwd())

from app.services.gemini_service import GeminiService

async def main():
    if len(sys.argv) < 2:
        print("Usage: python poc_script.py <pdf_path>")
        return

    pdf_path = sys.argv[1]
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print(f"Processing {pdf_path} in parallel...")
    
    try:
        with open(pdf_path, "rb") as f:
            content = f.read()
        
        service = GeminiService()
        result = await service.process_document_async(content, "test.pdf")
        
        print("\n--- Processing Complete ---")
        print(f"Doc Type: {result.doc_type}")
        print(f"Confidence: {result.confidence}")
        print(f"Pages Processed: {len(result.pages)}")
        print("Validation Warnings:", result.validation)
        
        for page in result.pages:
            print(f"\nPage {page.page_num} ({page.doc_type}):")
            print(f"  Fields: {str(page.fields)[:100]}...") # truncate for display

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
