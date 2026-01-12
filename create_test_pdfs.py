import fitz  # PyMuPDF

def create_credit_report(output_path="credit_report.pdf"):
    doc = fitz.open()
    page = doc.new_page()
    
    text = """
    CONFIDENTIAL CREDIT REPORT
    Source: Equifax
    Date: 2023-10-27
    
    Borrower: John Doe
    Address: 123 Maple St, Springfield
    
    CREDIT SCORE: 750 (FICO)
    
    Tradelines:
    - Chase Bank Credit Card: Balance $500
    - Auto Loan: Balance $12,000
    
    Total Debt: $12,500
    
    History:
    No lates in 24 months.
    """
    
    page.insert_text((50, 50), text, fontsize=12)
    doc.save(output_path)
    print(f"Created {output_path}")

def create_purchase_contract(output_path="purchase_contract.pdf"):
    doc = fitz.open()
    page = doc.new_page()
    
    text = """
    REAL ESTATE PURCHASE AGREEMENT
    
    This Sales Contract is made on 2023-11-01 between:
    
    Buyer: Alice Smith
    Seller: Bob Jones
    
    Property Address: 456 Oak Ave, Pleasantville, NY
    
    Purchase Price: $450,000.00
    Earnest Money: $5,000.00
    
    Closing Date: 2023-12-15
    
    Signatures:
    ____________________
    """
    
    page.insert_text((50, 50), text, fontsize=12)
    doc.save(output_path)
    print(f"Created {output_path}")

if __name__ == "__main__":
    create_credit_report()
    create_purchase_contract()
