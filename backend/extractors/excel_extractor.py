import os
import pandas as pd
from pathlib import Path

def find_header_row(file_path: str) -> int:
    """
    Acts as a scout. Reads the top of a CSV to find where the actual data starts
    by looking for the row with the most columns (commas).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Only read the first 20 lines so we don't waste memory on massive files
            lines = f.readlines()[:20]
            
        max_commas = 0
        header_index = 0
        
        # Check every line to find the one with the most data
        for i, line in enumerate(lines):
            comma_count = line.count(',')
            if comma_count > max_commas:
                max_commas = comma_count
                header_index = i
                
        return header_index
    except Exception:
        # If the scout fails for any reason, default to row 0
        return 0

def extract_text_from_tabular(file_path: str) -> str:
    """
    Safely loads CSV or Excel files, automatically skips dirty headers, 
    and converts them to a structured string format for LLM ingestion.
    """
    print(f"Processing spreadsheet: {os.path.basename(file_path)}...")
    ext = Path(file_path).suffix.lower()
    
    try:
        if ext == '.csv':
            # 1. Send the scout to find the real start line
            start_row = find_header_row(file_path)
            if start_row > 0:
                print(f"   -> [Auto-Fix] Detected junk headers. Skipping first {start_row} lines.")
            
            # 2. Tell Pandas to skip the junk, and warn us if a line is broken
            df = pd.read_csv(file_path, skiprows=start_row, on_bad_lines='warn')
            
        elif ext == '.xlsx':
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported tabular format: {ext}")
            
        # Enterprise Data Cleaning
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df.columns = pd.Series(df.columns).ffill()
        df = df.fillna("[BLANK]")
        
        structured_text = df.to_csv(index=False)
        return structured_text
        
    except Exception as e:
        print(f"❌ Failed to process {os.path.basename(file_path)}: {str(e)}")
        return ""


# ==========================================
# SELF-TESTING LAB
# ==========================================
if __name__ == "__main__":
    print("=== RUNNING ISOLATED UNIT TEST FOR TABULAR ENGINE ===")
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Use your dirty file to prove the auto-fix works!
    TEST_FILE = os.path.join(BASE_DIR, "data", "unzipped_files", "Historical_PnL.csv")
    
    try:
        if not os.path.exists(TEST_FILE):
            raise FileNotFoundError(f"Missing {TEST_FILE}!")
            
        result = extract_text_from_tabular(TEST_FILE)
        
        print("\n=== TEST PASSED: SPREADSHEET PROCESSED PERFECTLY ===")
        print("--- EXTRACTED STRUCTURE PREVIEW ---")
        print(result[:1000] if result else "[No data found]")
        print("-----------------------------------")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")