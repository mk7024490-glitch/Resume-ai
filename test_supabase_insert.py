from supabase import create_client, Client
import os

    # --- VERY IMPORTANT: Re-copy these from your Supabase Dashboard ---
    # Go to Project Settings > API and copy them again to be 100% sure.
SUPABASE_URL = "https://bfnyrphydrfvlhvzcqbb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmbnlycGh5ZHJmdmxodnpjcWJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg0MTY1ODQsImV4cCI6MjA3Mzk5MjU4NH0.TluIBY2ezX5rwewsbAOYmr-u0popL3JskIkI_HWmCEk"
    # --- End of section ---

try:
    print("Attempting to initialize Supabase client...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized.")

        # The data we want to insert
    test_resume_data = {
        "file_name": "test_from_script.txt",
        "storage_path": "public/test.txt",
        "raw_text": "This is a direct test."
    }

    print(f"\nAttempting to insert into 'resumes' table: {test_resume_data}")
        
        # Execute the insert command
    data, count = supabase.table("resumes").insert(test_resume_data).execute()

    print("\n--- RESULT ---")
        # Check for errors in the API response
    if hasattr(data[0], 'get') and data[0].get('error'):
         print(f"🔥 FAILED! Supabase returned an error: {data[0]['error']}")
    elif data and count is not None:
             print("✅ SUCCESS! Data was inserted successfully.")
             print(f"   Response Data: {data}")
    else:
         print("🤔 UNKNOWN RESPONSE. Something went wrong but no clear error.")
         print(data)

except Exception as e:
    print(f"\n--- CRITICAL ERROR ---")
    print(f"🔥 A Python exception occurred: {e}")
