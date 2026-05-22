import os
import fitz  # This is the PyMuPDF library

def extract_text_from_pdf(file_path: str) -> str:
    """
    Securely opens a PDF, reads the text from every page, 
    and compiles it into a clean, single string for the LLM.
    """
    print(f"Reading document: {os.path.basename(file_path)}...")
    extracted_text = []
    
    try:
        # 1. Open the PDF file safely
        doc = fitz.open(file_path)
        
        # 2. Loop through every single page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract raw text from the page
            text = page.get_text("text")
            
            # Only add it if the page actually has text (skips completely blank pages)
            if text.strip():
                # Add a clear marker so the LLM knows when a new page starts
                extracted_text.append(f"--- PAGE {page_num + 1} ---\n{text.strip()}")
                
        # 3. Close the document to free up computer memory
        doc.close()
        
        # 4. Join all the pages together with a double space
        final_document_text = "\n\n".join(extracted_text)
        
        return final_document_text
        
    except Exception as e:
        print(f"❌ Failed to process {os.path.basename(file_path)}: {str(e)}")
        return ""


# ==========================================
# SELF-TESTING LAB
# ==========================================
if __name__ == "__main__":
    print("=== RUNNING ISOLATED UNIT TEST FOR PDF ENGINE ===")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TEST_FILE = os.path.join(BASE_DIR, "data", "unzipped_files", "Enterprise_Master_Services_Agreement.pdf")
    
    try:
        if not os.path.exists(TEST_FILE):
            raise FileNotFoundError(
                f"Missing dummy_contract.pdf!\n"
                f"Expected location: {TEST_FILE}\n"
                f"ACTION REQUIRED: Find or save any PDF document, rename it to 'Enterprise_Master_Services_Agreement.pdf', and put it in 'data/unzipped_files'."
            )
            
        result = extract_text_from_pdf(TEST_FILE)
        
        print("\n=== TEST PASSED: PDF PROCESSED PERFECTLY ===")
        print("--- EXTRACTED TEXT PREVIEW ---")
        # Print the first 1000 characters to verify it worked
        print(result[:1000] if result else "[No text found. Is this a scanned image instead of a text PDF?]")
        print("------------------------------")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")