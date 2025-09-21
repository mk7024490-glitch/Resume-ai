# --- Core Flask & Supabase Imports ---
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import fitz  # PyMuPDF
from docx import Document
import io
import os
import json

# --- AI & Data Science Imports ---
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import fuzz
import numpy as np
import google.generativeai as genai # Gemini LLM library

# --- Local Imports ---
from config import SUPABASE_URL, SUPABASE_KEY, FLASK_ENV, GEMINI_API_KEY
from supabase import create_client, Client

# --- Application Setup ---
# The static_folder is set to '.' to serve index.html from the root 'backend' directory
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app) # Enable Cross-Origin Resource Sharing

# --- Client Initializations ---
supabase: Client = None
embedding_model = None
llm_model = None

try:
    # Initialize Supabase Client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully!")

    # Initialize Embedding Model (for semantic search)
    print("🤖 Loading Sentence Transformer model... (This may take a moment on first run)")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Embedding model loaded successfully.")

    # Initialize Generative LLM (for intelligent parsing)
    print("🤖 Initializing Generative AI model (Gemini)...")
    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel('gemini-pro')
    print("✅ Generative AI model initialized successfully.")

except Exception as e:
    print(f"🔥 A critical error occurred during initialization: {e}")

# ==============================================================================
# FRONTEND HOSTING
# ==============================================================================

@app.route('/')
def serve_index():
    """Serves the main index.html file to the user."""
    return send_from_directory('.', 'index.html')

# ==============================================================================
# LLM-POWERED PARSING FUNCTIONS
# ==============================================================================

def parse_jd_with_llm(jd_text: str) -> dict:
    """Uses Gemini to extract structured data from a Job Description."""
    if not llm_model: return {"error": "LLM not initialized"}
    
    prompt = """
    Analyze the following job description and return a clean JSON object.
    The JSON must have these keys: "job_title" (string), "must_have_skills" (list of strings),
    "good_to_have_skills" (list of strings), and "qualifications" (list of strings).
    If a value isn't found, use an empty list or empty string.

    Job Description:
    ---
    {text}
    ---
    """.format(text=jd_text)

    try:
        response = llm_model.generate_content(prompt)
        json_response = response.text.strip().replace('`', '').replace('json', '')
        return json.loads(json_response)
    except Exception as e:
        print(f"LLM JD Parsing Error: {e}")
        return {"error": f"Failed to parse JD with LLM: {str(e)}"}

def parse_resume_with_llm(resume_text: str) -> dict:
    """Uses Gemini to extract a list of skills from a Resume."""
    if not llm_model: return {"error": "LLM not initialized"}

    prompt = """
    Analyze the following resume text. Extract all technical skills, programming languages, 
    and software tools mentioned. Return a clean JSON object with one key: "skills" (a list of strings).

    Resume Text:
    ---
    {text}
    ---
    """.format(text=resume_text)
    
    try:
        response = llm_model.generate_content(prompt)
        json_response = response.text.strip().replace('`', '').replace('json', '')
        return json.loads(json_response)
    except Exception as e:
        print(f"LLM Resume Parsing Error: {e}")
        return {"error": f"Failed to parse resume with LLM: {str(e)}"}

# ==============================================================================
# FILE UPLOAD & PROCESSING ENDPOINTS
# ==============================================================================

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume_endpoint():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'}), 400
    
    filename = file.filename
    file_content = file.read()
    file_extension = ('.' + filename.rsplit('.', 1)[1].lower()) if '.' in filename else ''
    
    if file_extension == '.pdf': extracted_text = extract_text_from_pdf(file_content)
    elif file_extension == '.docx': extracted_text = extract_text_from_docx(file_content)
    else: return jsonify({'error': 'Unsupported file type'}), 400

    if "Error" in extracted_text: return jsonify({'error': extracted_text}), 500

    parsed_details = parse_resume_with_llm(extracted_text)
    if parsed_details.get("error"): return jsonify(parsed_details), 500

    try:
        storage_path = f"public/{filename}"
        supabase.storage.from_("resumes").upload(path=storage_path, file=file_content, file_options={"upsert": "true"})
        
        resume_response = supabase.table("resumes").insert({
            "file_name": filename, "storage_path": storage_path, "raw_text": extracted_text
        }).execute()
        new_resume_id = resume_response.data[0]['id']

        supabase.table("analysis_results").insert({
            "resume_id": new_resume_id, "extracted_skills": parsed_details.get("skills")
        }).execute()
        
        return jsonify({"message": "Resume analyzed with LLM.", "resume_id": new_resume_id, "parsed_details": parsed_details}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred with Supabase: {str(e)}"}), 500

@app.route('/analyze-jd', methods=['POST'])
def analyze_jd_endpoint():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'}), 400

    filename = file.filename
    file_content = file.read()
    file_extension = ('.' + filename.rsplit('.', 1)[1].lower()) if '.' in filename else ''

    if file_extension == '.pdf': extracted_text = extract_text_from_pdf(file_content)
    elif file_extension == '.docx': extracted_text = extract_text_from_docx(file_content)
    else: return jsonify({'error': 'Unsupported file type'}), 400

    if "Error" in extracted_text: return jsonify({'error': extracted_text}), 500
    
    parsed_details = parse_jd_with_llm(extracted_text)
    if parsed_details.get("error"): return jsonify(parsed_details), 500

    try:
        storage_path = f"public/{filename}"
        supabase.storage.from_("job_descriptions").upload(path=storage_path, file=file_content, file_options={"upsert": "true"})

        jd_response = supabase.table("job_descriptions").insert({
            "file_name": filename, "storage_path": storage_path, "raw_text": extracted_text,
            "job_title": parsed_details.get("job_title") # Assumes you added this column
        }).execute()
        new_jd_id = jd_response.data[0]['id']

        # Combine all skills for matching
        all_jd_skills = parsed_details.get("must_have_skills", []) + parsed_details.get("good_to_have_skills", [])
        supabase.table("jd_analysis_results").insert({
            "jd_id": new_jd_id, "required_skills": all_jd_skills
        }).execute()

        return jsonify({"message": "JD analyzed with LLM.", "jd_id": new_jd_id, "parsed_details": parsed_details}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred with Supabase: {str(e)}"}), 500

# ==============================================================================
# RELEVANCE ANALYSIS & DASHBOARD ENDPOINTS
# ==============================================================================
HARD_MATCH_WEIGHT = 0.40
SEMANTIC_MATCH_WEIGHT = 0.60
FUZZY_MATCH_THRESHOLD = 85

def perform_advanced_match(resume_data, jd_data):
    """Reusable function to calculate match score between a single resume and JD."""
    resume_text = resume_data.get('raw_text', '')
    jd_text = jd_data.get('raw_text', '')
    resume_skills = resume_data.get('analysis_results', [{}])[0].get('extracted_skills', []) or []
    jd_skills = jd_data.get('jd_analysis_results', [{}])[0].get('required_skills', []) or []
    
    # Step 1: Hard Match (Keyword & Fuzzy)
    matched_skills = set()
    if jd_skills:
        exact_matches = set(s.lower() for s in resume_skills) & set(s.lower() for s in jd_skills)
        matched_skills.update(exact_matches)
        remaining_jd = set(s.lower() for s in jd_skills) - exact_matches
        for jd_skill in remaining_jd:
            for res_skill in resume_skills:
                if fuzz.ratio(jd_skill, res_skill.lower()) > FUZZY_MATCH_THRESHOLD:
                    matched_skills.add(jd_skill)
                    break
    hard_score = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 100
    
    # Step 2: Semantic Match (Embeddings)
    resume_embedding = embedding_model.encode(resume_text)
    jd_embedding = embedding_model.encode(jd_text)
    semantic_score = cosine_similarity([resume_embedding], [jd_embedding])[0][0] * 100
    
    # Step 3: Weighted Final Score
    final_score = (hard_score * HARD_MATCH_WEIGHT) + (semantic_score * SEMANTIC_MATCH_WEIGHT)
    
    return round(final_score), hard_score, semantic_score, list(matched_skills), list(set(jd_skills) - matched_skills)

@app.route('/matches-for-jd/<jd_id>', methods=['GET'])
def get_matches_for_jd(jd_id):
    """Fetches all resumes, ranks them against a specific JD."""
    if not supabase: return jsonify({"error": "Database not available."}), 503
    try:
        jd_response = supabase.table("job_descriptions").select("*, jd_analysis_results(*)").eq("id", jd_id).single().execute()
        if not jd_response.data: return jsonify({"error": "JD not found."}), 404
        jd_data = jd_response.data

        resumes_response = supabase.table("resumes").select("*, analysis_results(*)").execute()
        if not resumes_response.data: return jsonify([]), 200

        ranked_candidates = []
        for resume in resumes_response.data:
            score, _, _, _, _ = perform_advanced_match(resume, jd_data)
            ranked_candidates.append({
                "resume_id": resume['id'], "file_name": resume['file_name'], "score": score
            })

        ranked_candidates.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(ranked_candidates), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/advanced-match/<resume_id>/<jd_id>', methods=['GET'])
def advanced_match_endpoint(resume_id, jd_id):
    """Gets a detailed breakdown for a single resume-JD pair."""
    if not supabase: return jsonify({"error": "Database not available."}), 503
    try:
        resume_response = supabase.table("resumes").select("*, analysis_results(*)").eq("id", resume_id).single().execute()
        jd_response = supabase.table("job_descriptions").select("*, jd_analysis_results(*)").eq("id", jd_id).single().execute()
        if not resume_response.data or not jd_response.data: return jsonify({"error": "Data not found."}), 404

        final_score, hard_score, semantic_score, matched, missing = perform_advanced_match(resume_response.data, jd_response.data)
        
        verdict = "Excellent Match" if final_score >= 85 else "Good Match" if final_score >= 70 else "Needs Review" if final_score >= 50 else "Poor Match"

        response_data = {
            "final_score": final_score, "verdict": verdict,
            "breakdown": {
                "hard_match_score": round(hard_score), "semantic_match_score": round(semantic_score),
                "matched_skills": sorted(matched), "missing_skills": sorted(missing),
            }
        }
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e: return f"Error extracting PDF text: {e}"

def extract_text_from_docx(file_content: bytes) -> str:
    try:
        doc = Document(io.BytesIO(file_content))
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e: return f"Error extracting DOCX text: {e}"

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == '__main__':
    # The app runs in debug mode if FLASK_ENV is not 'production'
    app.run(host='0.0.0.0', port=5000, debug=(FLASK_ENV != 'production'))
