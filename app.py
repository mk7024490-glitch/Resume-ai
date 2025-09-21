# --- Core Imports ---
from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz
from docx import Document
import io
import json

# --- AI & Data Science Imports ---
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import fuzz
import numpy as np
import google.generativeai as genai

# --- Local Imports ---
from config import SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY
from supabase import create_client, Client

# --- Application Setup ---
app = Flask(__name__)
CORS(app)

# --- Client Initializations ---
supabase: Client = None
embedding_model = None
llm_model = None

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized!")
    
    print("🤖 Loading Embedding model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Embedding model loaded.")

    print("🤖 Initializing Generative AI model (Gemini)...")
    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel('gemini-pro')
    print("✅ Generative AI model initialized.")
except Exception as e:
    print(f"🔥 A critical error occurred during initialization: {e}")

# --- Utility Functions ---
def extract_text(file_content, file_extension):
    text = ""
    try:
        if file_extension == '.pdf':
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                text = "".join(page.get_text() for page in doc)
        elif file_extension == '.docx':
            doc = Document(io.BytesIO(file_content))
            text = "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"Error extracting text: {e}"
    return text

def parse_with_llm(text, prompt_template):
    if not llm_model: return {"error": "LLM not initialized"}
    prompt = prompt_template.format(text=text)
    try:
        response = llm_model.generate_content(prompt)
        json_response = response.text.strip().replace('`', '').replace('json', '')
        return json.loads(json_response)
    except Exception as e:
        print(f"LLM Parsing Error: {e}")
        return {"error": f"Failed to parse with LLM: {str(e)}"}

# --- API Endpoints ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Backend is running and healthy"}), 200

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume_endpoint():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    filename = file.filename
    file_content = file.read()
    file_extension = ('.' + filename.rsplit('.', 1)[1].lower()) if '.' in filename else ''

    extracted_text = extract_text(file_content, file_extension)
    if "Error" in extracted_text: return jsonify({'error': extracted_text}), 500

    prompt = """Analyze the resume text. Extract all technical skills, programming languages, and tools. Return a JSON object with one key: "skills" (a list of strings). Resume Text: --- {text} ---"""
    parsed_details = parse_with_llm(extracted_text, prompt)
    if parsed_details.get("error"): return jsonify(parsed_details), 500

    try:
        storage_path = f"public/resumes/{filename}"
        supabase.storage.from_("resumes").upload(path=storage_path, file=file_content, file_options={"upsert": "true"})
        res_res = supabase.table("resumes").insert({"file_name": filename, "storage_path": storage_path, "raw_text": extracted_text}).execute()
        new_id = res_res.data[0]['id']
        supabase.table("analysis_results").insert({"resume_id": new_id, "extracted_skills": parsed_details.get("skills")}).execute()
        return jsonify({"message": "Resume analyzed with LLM.", "resume_id": new_id, "parsed_details": parsed_details}), 200
    except Exception as e: return jsonify({"error": f"Supabase error: {str(e)}"}), 500

@app.route('/analyze-jd', methods=['POST'])
def analyze_jd_endpoint():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    filename = file.filename
    file_content = file.read()
    file_extension = ('.' + filename.rsplit('.', 1)[1].lower()) if '.' in filename else ''
    
    extracted_text = extract_text(file_content, file_extension)
    if "Error" in extracted_text: return jsonify({'error': extracted_text}), 500
    
    prompt = """Analyze the job description. Return a JSON object with keys: "job_title", "must_have_skills", "good_to_have_skills", and "qualifications". Job Description: --- {text} ---"""
    parsed_details = parse_with_llm(extracted_text, prompt)
    if parsed_details.get("error"): return jsonify(parsed_details), 500

    try:
        storage_path = f"public/jds/{filename}"
        supabase.storage.from_("job_descriptions").upload(path=storage_path, file=file_content, file_options={"upsert": "true"})
        jd_res = supabase.table("job_descriptions").insert({"file_name": filename, "storage_path": storage_path, "raw_text": extracted_text, "job_title": parsed_details.get("job_title")}).execute()
        new_id = jd_res.data[0]['id']
        all_skills = parsed_details.get("must_have_skills", []) + parsed_details.get("good_to_have_skills", [])
        supabase.table("jd_analysis_results").insert({"jd_id": new_id, "required_skills": all_skills}).execute()
        return jsonify({"message": "JD analyzed with LLM.", "jd_id": new_id, "parsed_details": parsed_details}), 200
    except Exception as e: return jsonify({"error": f"Supabase error: {str(e)}"}), 500

def perform_advanced_match(resume_data, jd_data):
    resume_text = resume_data.get('raw_text', '')
    jd_text = jd_data.get('raw_text', '')
    resume_skills = resume_data.get('analysis_results', [{}])[0].get('extracted_skills', []) or []
    jd_skills = jd_data.get('jd_analysis_results', [{}])[0].get('required_skills', []) or []
    
    matched = set(s.lower() for s in resume_skills) & set(s.lower() for s in jd_skills)
    hard_score = (len(matched) / len(jd_skills)) * 100 if jd_skills else 100
    
    resume_emb = embedding_model.encode(resume_text)
    jd_emb = embedding_model.encode(jd_text)
    semantic_score = cosine_similarity([resume_emb], [jd_emb])[0][0] * 100
    
    final_score = (hard_score * 0.4) + (semantic_score * 0.6)
    
    return round(final_score)

@app.route('/matches-for-jd/<jd_id>', methods=['GET'])
def get_matches_for_jd(jd_id):
    try:
        jd_res = supabase.table("job_descriptions").select("*, jd_analysis_results(*)").eq("id", jd_id).single().execute()
        if not jd_res.data: return jsonify({"error": "JD not found."}), 404
        
        resumes_res = supabase.table("resumes").select("*, analysis_results(*)").execute()
        if not resumes_res.data: return jsonify([]), 200

        ranked_candidates = [
            {"resume_id": res['id'], "file_name": res['file_name'], "score": perform_advanced_match(res, jd_res.data)}
            for res in resumes_res.data
        ]
        
        ranked_candidates.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(ranked_candidates), 200
    except Exception as e: return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/advanced-match/<resume_id>/<jd_id>', methods=['GET'])
def advanced_match_endpoint(resume_id, jd_id):
    try:
        res_res = supabase.table("resumes").select("*, analysis_results(*)").eq("id", resume_id).single().execute()
        jd_res = supabase.table("job_descriptions").select("*, jd_analysis_results(*)").eq("id", jd_id).single().execute()
        if not res_res.data or not jd_res.data: return jsonify({"error": "Data not found."}), 404

        final_score = perform_advanced_match(res_res.data, jd_res.data)
        verdict = "Excellent Match" if final_score >= 85 else "Good Match" if final_score >= 70 else "Needs Review" if final_score >= 50 else "Poor Match"
        
        resume_skills = set(s.lower() for s in res_res.data.get('analysis_results', [{}])[0].get('extracted_skills', []) or [])
        jd_skills = set(s.lower() for s in jd_res.data.get('jd_analysis_results', [{}])[0].get('required_skills', []) or [])
        
        return jsonify({
            "final_score": final_score, "verdict": verdict,
            "breakdown": {"matched_skills": sorted(list(resume_skills & jd_skills)), "missing_skills": sorted(list(jd_skills - resume_skills))}
        }), 200
    except Exception as e: return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
