import requests
import os
import time

# --- Configuration ---
# The full URL to your running Flask application's endpoint
API_URL = "http://127.0.0.1:5000/analyze-resume"

# The folder where all your resume files are stored
RESUMES_FOLDER = "uploads"
# --- End of Configuration ---


def send_resume(file_path):
    """Sends a single resume file to the analysis API."""
    
    # Get the filename from the path
    filename = os.path.basename(file_path)
    
    print(f"--- Processing: {filename} ---")

    try:
        with open(file_path, 'rb') as f:
            # The key 'file' must match the key your Flask app expects (request.files['file'])
            files = {'file': (filename, f)}
            
            # Send the request
            response = requests.post(API_URL, files=files, timeout=30) # 30-second timeout
        
        # Check the response from the server
        if response.status_code == 200:
            print(f"✅ Success! Server response for {filename}:")
            # Print the JSON response from the server
            print(response.json())
        else:
            print(f"🔥 Error for {filename}. Status Code: {response.status_code}")
            print(f"   Server says: {response.text}")

    except FileNotFoundError:
        print(f"❌ Error: The file was not found at {file_path}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to the server at {API_URL}.")
        print("   Please make sure your Flask app ('app.py') is running.")
        return False # Stop the script if connection fails
    except requests.exceptions.RequestException as e:
        print(f"❌ An unexpected request error occurred for {filename}: {e}")
        
    print("-" * (len(filename) + 20) + "\n")
    return True


def main():
    """
    Finds all .pdf and .docx files in the RESUMES_FOLDER and sends them for analysis.
    """
    print(f"Starting resume upload process from folder: '{RESUMES_FOLDER}'")
    
    # Check if the folder exists
    if not os.path.isdir(RESUMES_FOLDER):
        print(f"Error: The folder '{RESUMES_FOLDER}' does not exist.")
        print("Please create it and place your resume files inside.")
        return

    # List all files in the directory
    try:
        files_in_folder = os.listdir(RESUMES_FOLDER)
    except Exception as e:
        print(f"Error reading files from the directory: {e}")
        return
        
    found_resumes = False
    for filename in files_in_folder:
        # Check for valid resume file extensions
        if filename.lower().endswith(('.pdf', '.docx')):
            found_resumes = True
            full_path = os.path.join(RESUMES_FOLDER, filename)
            
            # Send the file and check for connection errors
            if not send_resume(full_path):
                break # Stop if connection to server was lost
            
            time.sleep(1) # Wait 1 second between requests to not overload the server

    if not found_resumes:
        print(f"No .pdf or .docx files were found in the '{RESUMES_FOLDER}' folder.")
        
    print("--- Script finished ---")


if __name__ == "__main__":
    main()
