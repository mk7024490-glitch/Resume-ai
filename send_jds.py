import requests
import os
import time

# --- Configuration ---
# The folder containing the job description files you want to upload
JDS_FOLDER = "jds_to_upload" 
# The full URL to your running Flask application's new endpoint
API_ENDPOINT_URL = "http://127.0.0.1:5000/analyze-jd"

def upload_jds():
    """Finds all .pdf and .docx files in the JDS_FOLDER and sends them to the API."""
    print(f"Starting JD upload process from folder: '{JDS_FOLDER}'")

    if not os.path.isdir(JDS_FOLDER):
        print(f"🔥 Error: The folder '{JDS_FOLDER}' was not found. Please create it and add your JD files.")
        return

    # Find all supported files in the directory
    files_to_upload = [f for f in os.listdir(JDS_FOLDER) if f.lower().endswith(('.pdf', '.docx'))]

    if not files_to_upload:
        print(f"No .pdf or .docx files found in '{JDS_FOLDER}'.")
        return

    for filename in files_to_upload:
        file_path = os.path.join(JDS_FOLDER, filename)
        print(f"\n--- Processing: {filename} ---")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f)}
                response = requests.post(API_ENDPOINT_URL, files=files, timeout=30) # 30-second timeout
            
            if response.status_code == 200:
                print(f"✅ Success! Server response for {filename}:")
                print(response.json())
            else:
                print(f"🔥 Error for {filename}. Status Code: {response.status_code}")
                print(f"   Server says: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Could not connect to the server at {API_ENDPOINT_URL}.")
            print("   Please make sure your Flask app ('app.py') is running.")
            return # Stop the script if the server isn't running
        except Exception as e:
            print(f"An unexpected error occurred with {filename}: {e}")
        
        time.sleep(1) # Pause for a second between uploads

    print("\n--- Script finished ---")

if __name__ == "__main__":
    upload_jds()
