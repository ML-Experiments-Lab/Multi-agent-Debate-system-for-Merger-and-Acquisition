import os
import zipfile
from pathlib import Path

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

def route_files(extracted_file_paths: list[str]) -> dict:
    """Routes extracted files based on extension."""
    routing_report = {
        "tabular": [],
        "pdf": [],
        "image": [], # NEW: Added image bucket
        "quarantined": []
    }

    for file_path in extracted_file_paths:
        ext = Path(file_path).suffix.lower()

        if ext in ['.csv', '.xlsx']:
            routing_report["tabular"].append(file_path)
            print(f"[ROUTED] Tabular Engine -> {os.path.basename(file_path)}")

        elif ext == '.pdf':
            routing_report["pdf"].append(file_path)
            print(f"[ROUTED] Document Engine -> {os.path.basename(file_path)}")
            
        # NEW: Catch common image formats
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            routing_report["image"].append(file_path)
            print(f"[ROUTED] OCR Engine -> {os.path.basename(file_path)}")

        else:
            routing_report["quarantined"].append(file_path)
            print(f"[QUARANTINED] Unsupported type -> {os.path.basename(file_path)}")

    return routing_report

def process_upload(zip_filepath: str, extract_to_dir: str) -> dict:
    """Master function called by the API."""
    print(f"\n--- Starting File Ingestion ---")
    print(f"Unpacking Data Room: {zip_filepath}...")
    extracted_paths = extract_zip(zip_filepath, extract_to_dir)
    
    print(f"Successfully unpacked {len(extracted_paths)} files. Routing to extractors...")
    report = route_files(extracted_paths)
    
    return report


# ==========================================
# SELF-TESTING LAB (Runs only when executed directly)
# ==========================================
if __name__ == "__main__":
    print("=== RUNNING ISOLATED UNIT TEST FOR FILE ROUTER ===")
    
    # 1. Dynamically set paths so it works on any computer
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TEST_ZIP = os.path.join(BASE_DIR, "data", "raw_uploads", "dummy_data_room.zip")
    EXTRACT_DIR = os.path.join(BASE_DIR, "data", "unzipped_files")
    
    # 2. Strict Execution Check
    try:
        # Check if the test file even exists before running
        if not os.path.exists(TEST_ZIP):
            raise FileNotFoundError(
                f"Missing dummy_data_room.zip!\n"
                f"Expected location: {TEST_ZIP}\n"
                f"ACTION REQUIRED: Create 5 dummy files, zip them, and place them in the folder above."
            )
            
        # Run the core logic
        final_report = process_upload(TEST_ZIP, EXTRACT_DIR)
        
        # Output results
        print("\n=== TEST PASSED: SCRIPT EXECUTED PERFECTLY ===")
        print(f"Total PDFs found: {len(final_report['pdf'])}")
        print(f"Total Tabular found: {len(final_report['tabular'])}")
        print(f"Total Quarantined: {len(final_report['quarantined'])}")
        
    except Exception as e:
        # If ANYTHING goes wrong (bad zip, wrong path, missing library), it catches it here
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")