import pandas as pd
import sqlite3
import os

def build_engine():
    print("🚀 Running Universal Data Pipeline...")
    
    # Matching your exact filename from the terminal
    csv_file = 'data/layoffs.csv.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} still not found!")
        return

    df = pd.read_csv(csv_file)

    # --- THE FIX: SMART COLUMN DETECTION ---
    # Convert all column names to lowercase so we don't have to worry about 'Employees' vs 'employees'
    df.columns = [c.lower() for c in df.columns]
    print(f"Detected columns: {list(df.columns)}")

    # Check for common names for the 'Employees' column
    if 'employees' in df.columns:
        df['employees'] = df['employees'].fillna(0)
    elif 'total_emp' in df.columns:
        df['employees'] = df['total_emp'].fillna(0)
    else:
        # If we can't find it, we'll use the first numeric column we find
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            df['employees'] = df[numeric_cols[0]].fillna(0)
            print(f"⚠️ Using '{numeric_cols[0]}' as the employee count column.")

    # Check for date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # --- LOAD TO SQL ---
    conn = sqlite3.connect('layoffs.db')
    df.to_sql('layoffs_table', conn, if_exists='replace', index=False)
    conn.close()
    
    print("✅ Success! 'layoffs.db' is ready for your dashboard.")

if __name__ == "__main__":
    build_engine()