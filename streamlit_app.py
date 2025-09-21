import streamlit as st
import requests
import pandas as pd
import time

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:5000"

# --- Page Configuration ---
st.set_page_config(page_title="ResumeAI Dashboard", layout="wide")

# --- Styling ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'jd_list' not in st.session_state:
    st.session_state.jd_list = []
if 'selected_jd' not in st.session_state:
    st.session_state.selected_jd = None
if 'ranked_candidates' not in st.session_state:
    st.session_state.ranked_candidates = pd.DataFrame()

# --- API Functions ---
def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def get_jds_from_db():
    # In a real app, you'd fetch this from Supabase. We'll simulate for now.
    # This part needs a new backend endpoint to be fully functional.
    pass # We will populate this from the sidebar upload

def upload_file(endpoint, uploaded_file):
    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        response = requests.post(f"{BACKEND_URL}/{endpoint}", files=files)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def get_ranked_candidates(jd_id):
    try:
        response = requests.get(f"{BACKEND_URL}/matches-for-jd/{jd_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# --- UI Components ---
def sidebar():
    with st.sidebar:
        st.header("ResumeAI ⚡")
        st.markdown("---")
        
        st.subheader("Upload Job Description")
        uploaded_jd = st.file_uploader("Upload a JD (PDF or DOCX)", type=['pdf', 'docx'], key="jd_uploader")
        if uploaded_jd:
            with st.spinner("Analyzing JD..."):
                result = upload_file("analyze-jd", uploaded_jd)
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"JD '{uploaded_jd.name}' analyzed!")
                    # Add to a temporary list for this session
                    st.session_state.jd_list.append({"file_name": uploaded_jd.name, "id": result.get("jd_id")})

        st.markdown("---")
        st.subheader("Upload Resume")
        uploaded_resume = st.file_uploader("Upload a Resume (PDF or DOCX)", type=['pdf', 'docx'], key="resume_uploader")
        if uploaded_resume:
            with st.spinner("Analyzing Resume..."):
                result = upload_file("analyze-resume", uploaded_resume)
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"Resume '{uploaded_resume.name}' analyzed!")
                    # If a JD is selected, refresh the ranked list
                    if st.session_state.selected_jd:
                        candidates = get_ranked_candidates(st.session_state.selected_jd['id'])
                        if "error" not in candidates:
                            st.session_state.ranked_candidates = pd.DataFrame(candidates)
                        else:
                            st.error(f"Could not refresh candidates: {candidates['error']}")

        st.markdown("---")
        backend_status = "🟢 Connected" if check_backend() else "🔴 Disconnected"
        st.caption(f"Backend Status: {backend_status}")

def main_dashboard():
    st.title("Placement Team Dashboard")
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Select Job Description")
        if not st.session_state.jd_list:
            st.info("Upload a Job Description using the sidebar to begin.")
        else:
            jd_options = {jd['file_name']: jd for jd in st.session_state.jd_list}
            selected_jd_name = st.radio("Available Jobs", list(jd_options.keys()))
            
            if selected_jd_name:
                st.session_state.selected_jd = jd_options[selected_jd_name]

    with col2:
        st.subheader("Ranked Candidates")
        if st.session_state.selected_jd:
            jd = st.session_state.selected_jd
            st.markdown(f"Showing candidates for: **{jd['file_name']}**")
            
            with st.spinner("Fetching ranked candidates..."):
                candidates = get_ranked_candidates(jd['id'])
                if "error" in candidates:
                    st.error(f"Could not load candidates: {candidates['error']}")
                elif not candidates:
                    st.warning("No resumes have been uploaded and analyzed for this job yet.")
                else:
                    st.session_state.ranked_candidates = pd.DataFrame(candidates)
                    
                    # Display the ranked list
                    df = st.session_state.ranked_candidates
                    for index, row in df.iterrows():
                        expander = st.expander(f"**{row['file_name']}** - Score: {row['score']}%")
                        with expander:
                            st.write(f"Detailed analysis for {row['file_name']}:")
                            # Placeholder for detailed view - can be fetched on demand
                            st.info("Click a button to fetch detailed breakdown.")
                            if st.button("Get Match Details", key=f"details_{row['resume_id']}"):
                                with st.spinner("Fetching details..."):
                                    details_res = requests.get(f"{BACKEND_URL}/advanced-match/{row['resume_id']}/{jd['id']}")
                                    if details_res.ok:
                                        details = details_res.json()
                                        st.json(details)
                                    else:
                                        st.error("Could not fetch details.")
        else:
            st.info("Select a job from the left to see ranked candidates.")

# --- Main App Execution ---
sidebar()
main_dashboard()
