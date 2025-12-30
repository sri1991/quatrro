from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PageData(BaseModel):
    page_num: int
    doc_type: str
    fields: Dict[str, Any]

class ExtractionResult(BaseModel):
    doc_type: str
    confidence: float
    pages: List[PageData]
    validation: List[str]
    raw_response: Optional[str] = None
