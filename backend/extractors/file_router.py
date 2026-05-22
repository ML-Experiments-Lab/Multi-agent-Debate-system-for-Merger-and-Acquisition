import os
import zipfile
from pathlib import Path

# ==========================================
# IMPORTING YOUR EXTRACTION ENGINES
# ==========================================
# We use absolute imports assuming you run this from the root project folder
from backend.extractors.pdf_extractor import extract_text_from_pdf
from backend.extractors.excel_extractor import extract_text_from_tabular
from backend.extractors.image_extractor import extract_text_from_image

def extract_zip(zip_filepath: str, extract_to_dir: str) -> list[str]:
    """
    Safely extracts a ZIP file to a target directory and returns a list of extracted file paths.
    """
    os.makedirs(extract_to_dir, exist_ok=True)
    extracted_files = []
    
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(extract_to_dir)
        for file_info in zip_ref.infolist():
            # Skip directories, only capture files
            if not file_info.is_dir():
                extracted_files.append(os.path.join(extract_to_dir, file_info.filename))
                
    return extracted_files

def route_and_extract(extracted_file_paths: list[str]) -> dict:
    """
    Routes files to the correct engine AND extracts the text into a master dictionary.
    """
    master_diligence_report = {
        "documents": {},  # Stores PDF text
        "tabular": {},    # Stores CSV/Excel text
        "images": {},     # Stores OCR text
        "quarantined": [] # Stores unsafe files
    }

    for file_path in extracted_file_paths:
        ext = Path(file_path).suffix.lower()
        filename = os.path.basename(file_path)

        # 1. Tabular Routing & Extraction
        if ext in ['.csv', '.xlsx']:
            print(f"[ROUTING] Sending {filename} to Tabular Engine...")
            text = extract_text_from_tabular(file_path)
            master_diligence_report["tabular"][filename] = text

        # 2. PDF Routing & Extraction
        elif ext == '.pdf':
            print(f"[ROUTING] Sending {filename} to Document Engine...")
            text = extract_text_from_pdf(file_path)
            master_diligence_report["documents"][filename] = text
            
        # 3. Image Routing & Extraction
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            print(f"[ROUTING] Sending {filename} to OCR Engine...")
            text = extract_text_from_image(file_path)
            master_diligence_report["images"][filename] = text

        # 4. Quarantine
        else:
            print(f"[QUARANTINED] Unsupported type -> {filename}")
            master_diligence_report["quarantined"].append(filename)

    return master_diligence_report

def process_upload(zip_filepath: str, extract_to_dir: str) -> dict:
    """Master function called by the API."""
    print(f"\n--- Starting Master Diligence Pipeline ---")
    print(f"Unpacking Data Room: {zip_filepath}...")
    
    extracted_paths = extract_zip(zip_filepath, extract_to_dir)
    print(f"Successfully unpacked {len(extracted_paths)} files. Firing up engines...\n")
    
    final_report = route_and_extract(extracted_paths)
    
    return final_report


# ==========================================
# SELF-TESTING LAB (System Integration Test)
# ==========================================
if __name__ == "__main__":
    print("=== RUNNING SYSTEM INTEGRATION TEST ===")
    
    # Dynamically set paths so it works on any computer
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # If your file_router is inside the backend folder, we step back one more level to reach the root
    if os.path.basename(BASE_DIR) == "backend":
        BASE_DIR = os.path.dirname(BASE_DIR)
        
    TEST_ZIP = os.path.join(BASE_DIR, "data", "raw_uploads", "dummy_data_room.zip")
    EXTRACT_DIR = os.path.join(BASE_DIR, "data", "unzipped_files")
    
    try:
        # Strict Execution Check
        if not os.path.exists(TEST_ZIP):
            raise FileNotFoundError(
                f"Missing dummy_data_room.zip!\n"
                f"Expected location: {TEST_ZIP}\n"
                f"ACTION REQUIRED: Zip your dummy pdf, csv, and jpg into one file named 'dummy_data_room.zip' and put it in 'data/raw_uploads'."
            )
            
        # Run the core logic
        report = process_upload(TEST_ZIP, EXTRACT_DIR)
        
        # Output results
        print("\n=== PIPELINE EXECUTION COMPLETE ===")
        print(f"Total PDFs extracted: {len(report['documents'])}")
        print(f"Total Spreadsheets extracted: {len(report['tabular'])}")
        print(f"Total Images extracted: {len(report['images'])}")
        print(f"Total Quarantined: {len(report['quarantined'])}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")