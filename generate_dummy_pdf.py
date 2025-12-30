import fitz

doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Mortgage Document - Form 1040", fontsize=20)
page.insert_text((50, 100), "Borrower Name: John Doe", fontsize=12)
page.insert_text((50, 120), "SSN: 123-45-6789", fontsize=12)
page.insert_text((50, 140), "Income: $50,000", fontsize=12)
doc.save("dummy_loan_package.pdf")
print("Created dummy_loan_package.pdf")
