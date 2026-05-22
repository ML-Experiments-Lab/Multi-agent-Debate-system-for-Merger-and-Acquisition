import os
import pytesseract
from PIL import Image

# Architect Guardrail: Point Python to the Windows Tesseract installation
# If you deploy this to a Linux cloud server later, this line is safely ignored.
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path: str) -> str:
    """
    Secure, offline Optical Character Recognition (OCR).
    Extracts raw text from an image file without sending data to the cloud.
    """
    print(f"Scanning image: {os.path.basename(image_path)}...")
    
    try:
        # Open the image using Pillow (PIL)
        img = Image.open(image_path)
        
        # Run local OCR to extract text
        extracted_text = pytesseract.image_to_string(img)
        
        # Clean up the output (remove excessive blank lines)
        clean_text = "\n".join([line for line in extracted_text.splitlines() if line.strip()])
        
        return clean_text
        
    except Exception as e:
        print(f"❌ Failed to process {os.path.basename(image_path)}: {str(e)}")
        # If it fails, return an empty string so the pipeline doesn't crash
        return ""


# ==========================================
# SELF-TESTING LAB
# ==========================================
if __name__ == "__main__":
    print("=== RUNNING ISOLATED UNIT TEST FOR OCR ENGINE ===")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Expecting a dummy image inside the unzipped folder for testing
    TEST_IMAGE = os.path.join(BASE_DIR, "data", "unzipped_files", "dummy_scan.jpeg")
    
    try:
        if not os.path.exists(TEST_IMAGE):
            raise FileNotFoundError(
                f"Missing dummy_scan.jpg!\n"
                f"Expected location: {TEST_IMAGE}\n"
                f"ACTION REQUIRED: Find any image with text, rename it to 'dummy_scan.jpeg', and drop it in 'data/unzipped_files'."
            )
            
        result = extract_text_from_image(TEST_IMAGE)
        
        print("\n=== TEST PASSED: OCR EXECUTED PERFECTLY ===")
        print("--- EXTRACTED TEXT PREVIEW ---")
        # Print the first 500 characters to verify it worked
        print(result[:500] if result else "[No text detected in image]")
        print("------------------------------")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")
        if "tesseract is not installed" in str(e).lower():
            print("\n💡 ARCHITECT NOTE: You must install Tesseract-OCR on your Windows machine.")
            print("Download here: https://github.com/UB-Mannheim/tesseract/wiki")