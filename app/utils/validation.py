import re
from typing import List, Dict, Any

def validate_extraction(data: Dict[str, Any]) -> List[str]:
    warnings = []
    
    # Extract fields from all pages
    all_fields = {}
    if "pages" in data:
        for page in data["pages"]:
            all_fields.update(page.get("fields", {}))
    
    # Example validation: SSN format
    ssn = all_fields.get("ssn")
    if ssn:
        # Basic regex for SSN: XXX-XX-XXXX
        if not re.match(r"^\d{3}-\d{2}-\d{4}$", str(ssn)):
            warnings.append("Invalid SSN format")
            
    # Example validation: Income > 0
    income_lines = all_fields.get("income_lines", [])
    if isinstance(income_lines, list):
         for income in income_lines:
             amount = income.get("amount")
             if amount and isinstance(amount, (int, float)) and amount <= 0:
                 warnings.append("Income amount must be greater than 0")

    return warnings
