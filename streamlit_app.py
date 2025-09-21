import streamlit as st
import requests
import json
import time
import random
from datetime import datetime
import pandas as pd
import os
from typing import Dict, List, Optional, Any
import json

# --- Configuration ---
st.set_page_config(
    page_title="ResumeAI - AI-Powered Hiring",
    page_icon="📄",
    layout="wide"
)

# --- Custom CSS for dark theme ---
st.markdown("""
<style>
    /* Dark theme colors */
    :root {
        --background-color: #030712;  /* bg-gray-950 */
        --sidebar-bg: #111827;        /* bg-gray-900 */
        --card-bg: #1f2937;           /* bg-gray-800 */
        --accent-color: #2563eb;      /* bg-blue-600 */
        --text-color: #f3f4f6;        /* text-gray-100 */
        --text-secondary: #9ca3af;    /* text-gray-400 */
    }
    
    /* Main background */
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid #374151;
    }
    
    /* Card styling */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div[data-testid="element-container"] {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 6px;
    }
    
    /* Text colors */
    h1, h2, h3, p {
        color: var(--text-color) !important;
    }
    
    /* Metric styling */
    div[data-testid="stMetric"] {
        background-color: var(--card-bg);
        padding: 1rem;
        border-radius: 8px;
    }
    
    /* Container styling */
    [data-testid="stContainer"] {
        background-color: var(--card-bg);
        border-radius: 8px;
        border: 1px solid #374151 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Type Definitions (for documentation) ---
# JobPosition: id, file_name, job_title
# RankedCandidate: resume_id, file_name, score
# MatchDetails: final_score, verdict, breakdown (matched_skills, missing_skills)

# --- Constants ---
BACKEND_URL = "http://127.0.0.1:5000"

# --- Session State Initialization ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"
if 'job_positions' not in st.session_state:
    st.session_state.job_positions = []
if 'ranked_candidates' not in st.session_state:
    st.session_state.ranked_candidates = []
if 'selected_jd_id' not in st.session_state:
    st.session_state.selected_jd_id = ""
if 'backend_error' not in st.session_state:
    st.session_state.backend_error = None
if 'modal_data' not in st.session_state:
    st.session_state.modal_data = None
if 'show_create_job_modal' not in st.session_state:
    st.session_state.show_create_job_modal = False
if 'stats' not in st.session_state:
    st.session_state.stats = {
        "total_resumes": 42,
        "total_jobs": 8,
        "matches_today": 12,
        "avg_score": 76
    }
if 'recent_evaluations' not in st.session_state:
    st.session_state.recent_evaluations = [
        {"id": "1", "title": "Senior Software Engineer", "date": "Today", "matches": 8},
        {"id": "2", "title": "Product Manager", "date": "Yesterday", "matches": 5},
        {"id": "3", "title": "UX Designer", "date": "2 days ago", "matches": 7}
    ]

# --- API Functions ---
def fetch_jds():
    st.session_state.backend_error = None
    try:
        response = requests.get(f"{BACKEND_URL}/jds")
        if response.status_code != 200:
            raise Exception(f"HTTP error! status: {response.status_code}")
        st.session_state.job_positions = response.json()
    except Exception as e:
        st.session_state.backend_error = "Failed to connect to the backend. Please ensure the Python server is running on http://127.0.0.1:5000 and try again."
        st.error(st.session_state.backend_error)

def fetch_ranked_candidates(jd_id: str):
    if not jd_id:
        return
    
    st.session_state.ranked_candidates = []
    try:
        response = requests.get(f"{BACKEND_URL}/matches-for-jd/{jd_id}")
        if response.status_code != 200:
            raise Exception("Failed to fetch candidates")
        st.session_state.ranked_candidates = response.json()
    except Exception as e:
        st.session_state.backend_error = "Failed to fetch candidates. Please check the backend server."
        st.error(st.session_state.backend_error)

def fetch_match_details(resume_id: str, jd_id: str):
    if not resume_id or not jd_id:
        return
    
    try:
        response = requests.get(f"{BACKEND_URL}/advanced-match/{resume_id}/{jd_id}")
        if response.status_code != 200:
            raise Exception("Failed to fetch match details")
        st.session_state.modal_data = response.json()
    except Exception as e:
        st.error("Failed to fetch match details")
        st.session_state.modal_data = None

def handle_file_upload(file, file_type: str):
    if file is None:
        return
    
    files = {"file": (file.name, file.getvalue(), file.type)}
    endpoint = 'analyze-resume' if file_type == 'resume' else 'analyze-jd'
    
    try:
        response = requests.post(f"{BACKEND_URL}/{endpoint}", files=files)
        if response.status_code != 200:
            raise Exception(f"Failed to upload {file_type}")
        
        if file_type == 'jd':
            fetch_jds()
        if file_type == 'resume' and st.session_state.selected_jd_id:
            fetch_ranked_candidates(st.session_state.selected_jd_id)
            
        st.success(f"{file_type.capitalize()} uploaded successfully!")
    except Exception as e:
        st.error(f"Failed to upload {file_type}. Is the backend server running?")

def change_page(page: str):
    st.session_state.current_page = page

def select_job_position(jd_id: str):
    st.session_state.selected_jd_id = jd_id
    fetch_ranked_candidates(jd_id)
    st.session_state.current_page = "evaluations"

# --- UI Components ---
def sidebar():
    with st.sidebar:
        # Logo and title
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
                <div style="background-color: #2563eb; width: 40px; height: 40px; border-radius: 8px; 
                display: flex; align-items: center; justify-content: center; margin-top: 5px;">
                    <span style="color: white; font-size: 20px;">📄</span>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <h2 style="margin-bottom: 0; color: white; font-weight: 600;">ResumeAI</h2>
                <p style="margin-top: 0; color: #9ca3af; font-size: 0.9em;">AI-Powered Hiring</p>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown('<p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 10px;">NAVIGATION</p>', unsafe_allow_html=True)
        
        # Dashboard button
        dashboard_btn = """
        <div style="display: flex; align-items: center; padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; 
        background-color: {bg_color}; color: {text_color}; cursor: pointer;">
            <span style="margin-right: 12px;">📊</span>
            <span>Dashboard</span>
        </div>
        """
        
        # Upload button
        upload_btn = """
        <div style="display: flex; align-items: center; padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; 
        background-color: {bg_color}; color: {text_color}; cursor: pointer;">
            <span style="margin-right: 12px;">📤</span>
            <span>Upload Resume</span>
        </div>
        """
        
        # Evaluations button with notification badge
        eval_btn = """
        <div style="display: flex; align-items: center; padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; 
        background-color: {bg_color}; color: {text_color}; cursor: pointer; position: relative;">
            <span style="margin-right: 12px;">📝</span>
            <span>Evaluations</span>
            <span style="background-color: #2563eb; color: white; border-radius: 9999px; padding: 2px 8px; 
            font-size: 0.7em; margin-left: auto;">24</span>
        </div>
        """
        
        # Positions button
        positions_btn = """
        <div style="display: flex; align-items: center; padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; 
        background-color: {bg_color}; color: {text_color}; cursor: pointer;">
            <span style="margin-right: 12px;">💼</span>
            <span>Job Positions</span>
        </div>
        """
        
        # Settings button
        settings_btn = """
        <div style="display: flex; align-items: center; padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; 
        background-color: {bg_color}; color: {text_color}; cursor: pointer;">
            <span style="margin-right: 12px;">⚙️</span>
            <span>Settings</span>
        </div>
        """
        
        # Render buttons with appropriate styling based on current page
        st.markdown(dashboard_btn.format(
            bg_color="#2563eb" if st.session_state.current_page == "dashboard" else "transparent",
            text_color="white" if st.session_state.current_page == "dashboard" else "#9ca3af"
        ), unsafe_allow_html=True)
        if st.button("Dashboard", key="btn_dashboard", use_container_width=True, type="secondary", help="Go to Dashboard"):
            change_page("dashboard")
            st.rerun()
            
        st.markdown(upload_btn.format(
            bg_color="#2563eb" if st.session_state.current_page == "upload" else "transparent",
            text_color="white" if st.session_state.current_page == "upload" else "#9ca3af"
        ), unsafe_allow_html=True)
        if st.button("Upload Resume", key="btn_upload", use_container_width=True, type="secondary", help="Upload new resumes"):
            change_page("upload")
            st.rerun()
            
        st.markdown(eval_btn.format(
            bg_color="#2563eb" if st.session_state.current_page == "evaluations" else "transparent",
            text_color="white" if st.session_state.current_page == "evaluations" else "#9ca3af"
        ), unsafe_allow_html=True)
        if st.button("Evaluations", key="btn_evaluations", use_container_width=True, type="secondary", help="View candidate evaluations"):
            change_page("evaluations")
            st.rerun()
            
        st.markdown(positions_btn.format(
            bg_color="#2563eb" if st.session_state.current_page == "positions" else "transparent",
            text_color="white" if st.session_state.current_page == "positions" else "#9ca3af"
        ), unsafe_allow_html=True)
        if st.button("Job Positions", key="btn_positions", use_container_width=True, type="secondary", help="Manage job positions"):
            change_page("positions")
            st.rerun()
            
        st.markdown(settings_btn.format(
            bg_color="#2563eb" if st.session_state.current_page == "settings" else "transparent",
            text_color="white" if st.session_state.current_page == "settings" else "#9ca3af"
        ), unsafe_allow_html=True)
        if st.button("Settings", key="btn_settings", use_container_width=True, type="secondary", help="Configure application settings"):
            change_page("settings")
            st.rerun()
            
        # Footer
        st.markdown("""
            <div style="position: absolute; bottom: 20px; left: 20px; right: 20px; text-align: center;">
                <p style="color: #6b7280; font-size: 0.8em;">© 2023 ResumeAI. All rights reserved.</p>
            </div>
        """, unsafe_allow_html=True)

def error_display():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.error("Connection Error")
        st.write(st.session_state.backend_error)
        if st.button("Retry Connection", type="primary"):
            fetch_jds()

def dashboard_page():
    st.markdown("<h1 style='color: white; font-weight: 600;'>Dashboard</h1>", unsafe_allow_html=True)
    
    # Statistics Cards
    st.markdown("<p style='color: #9ca3af; margin-bottom: 10px;'>OVERVIEW</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Resumes Card
    with col1:
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 5px;">Total Resumes</p>
                    <h2 style="color: white; margin: 0;">{}</h2>
                </div>
                <div style="background-color: rgba(37, 99, 235, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="color: #2563eb; font-size: 1.2em;">📄</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <span style="color: #10b981; font-size: 0.8em; display: flex; align-items: center;">
                    <span style="margin-right: 4px;">↑</span> 12%
                </span>
                <span style="color: #9ca3af; font-size: 0.8em; margin-left: 5px;">from last month</span>
            </div>
        </div>
        """.format(st.session_state.stats["total_resumes"]), unsafe_allow_html=True)
    
    # Matched Candidates Card
    with col2:
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 5px;">Matched Candidates</p>
                    <h2 style="color: white; margin: 0;">{}</h2>
                </div>
                <div style="background-color: rgba(37, 99, 235, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="color: #2563eb; font-size: 1.2em;">👥</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <span style="color: #10b981; font-size: 0.8em; display: flex; align-items: center;">
                    <span style="margin-right: 4px;">↑</span> 18%
                </span>
                <span style="color: #9ca3af; font-size: 0.8em; margin-left: 5px;">from last month</span>
            </div>
        </div>
        """.format(st.session_state.stats["matches_today"]), unsafe_allow_html=True)
    
    # Active Jobs Card
    with col3:
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 5px;">Active Jobs</p>
                    <h2 style="color: white; margin: 0;">{}</h2>
                </div>
                <div style="background-color: rgba(37, 99, 235, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="color: #2563eb; font-size: 1.2em;">💼</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <span style="color: #10b981; font-size: 0.8em; display: flex; align-items: center;">
                    <span style="margin-right: 4px;">↑</span> 5%
                </span>
                <span style="color: #9ca3af; font-size: 0.8em; margin-left: 5px;">from last month</span>
            </div>
        </div>
        """.format(st.session_state.stats["total_jobs"]), unsafe_allow_html=True)
    
    # Success Rate Card
    with col4:
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 5px;">Success Rate</p>
                    <h2 style="color: white; margin: 0;">{}%</h2>
                </div>
                <div style="background-color: rgba(37, 99, 235, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="color: #2563eb; font-size: 1.2em;">📈</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; margin-top: 15px;">
                <span style="color: #10b981; font-size: 0.8em; display: flex; align-items: center;">
                    <span style="margin-right: 4px;">↑</span> 7%
                </span>
                <span style="color: #9ca3af; font-size: 0.8em; margin-left: 5px;">from last month</span>
            </div>
        </div>
        """.format(st.session_state.stats["avg_score"]), unsafe_allow_html=True)
    
    # Recent Evaluations and Quick Actions
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div class="card" style="height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: white; margin: 0;">Recent Evaluations</h3>
                <span style="color: #2563eb; cursor: pointer; font-size: 0.9em;">View All</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Recent evaluations list
        for eval in st.session_state.recent_evaluations:
            st.markdown(f"""
            <div style="padding: 12px; background-color: #1f2937; border-radius: 6px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: white; margin: 0; font-size: 1em;">{eval['title']}</h4>
                        <p style="color: #9ca3af; margin: 5px 0 0 0; font-size: 0.8em;">
                            {eval['matches']} candidates • {eval['date']}
                        </p>
                    </div>
                    <div>
                        <span style="background-color: #2563eb; color: white; 
                        padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">Active</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div class="card" style="height: 100%;">
            <h3 style="color: white; margin: 0 0 15px 0;">Quick Actions</h3>
            
            <button style="background-color: #2563eb; color: white; border: none; padding: 10px; 
            border-radius: 6px; width: 100%; text-align: left; margin-bottom: 15px; cursor: pointer;">
                <span style="margin-right: 8px;">📤</span> Upload New Resume
            </button>
            
            <button style="background-color: #374151; color: white; border: none; padding: 10px; 
            border-radius: 6px; width: 100%; text-align: left; margin-bottom: 15px; cursor: pointer;">
                <span style="margin-right: 8px;">➕</span> Create New Job
            </button>
            
            <h4 style="color: white; margin: 20px 0 10px 0; font-size: 0.9em;">PROCESSING</h4>
            
            <div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #9ca3af; font-size: 0.8em;">Resume Analysis</span>
                    <span style="color: white; font-size: 0.8em;">75%</span>
                </div>
                <div style="background-color: #374151; border-radius: 9999px; height: 6px; width: 100%;">
                    <div style="background-color: #2563eb; border-radius: 9999px; height: 6px; width: 75%;"></div>
                </div>
            </div>
            
            <div style="margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #9ca3af; font-size: 0.8em;">Job Matching</span>
                    <span style="color: white; font-size: 0.8em;">45%</span>
                </div>
                <div style="background-color: #374151; border-radius: 9999px; height: 6px; width: 100%;">
                    <div style="background-color: #2563eb; border-radius: 9999px; height: 6px; width: 45%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def positions_page():
    st.markdown("<h1 style='color: white; font-weight: 600;'>Job Positions</h1>", unsafe_allow_html=True)
    
    # Header with buttons
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.text_input("Search positions...", placeholder="Search by title, department, or skills", label_visibility="collapsed")
    
    with col2:
        if st.button("Upload JD", use_container_width=True):
            st.session_state.show_upload_jd = True
    
    with col3:
        if st.button("Create Job", use_container_width=True):
            st.session_state.show_create_job_modal = True
    
    # Job positions grid
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mock job positions
    job_positions = [
        {
            "title": "Senior Software Engineer",
            "status": "Active",
            "status_color": "#10b981",
            "department": "Engineering",
            "location": "San Francisco, CA",
            "salary": "$120,000 - $150,000",
            "applicants": 24,
            "date": "Posted 2 weeks ago",
            "description": "We're looking for an experienced software engineer to join our team and help build scalable web applications.",
            "skills": ["Python", "React", "AWS", "Microservices"]
        },
        {
            "title": "Product Manager",
            "status": "Active",
            "status_color": "#10b981",
            "department": "Product",
            "location": "Remote",
            "salary": "$110,000 - $140,000",
            "applicants": 18,
            "date": "Posted 1 week ago",
            "description": "Seeking a product manager to lead our product development process and work closely with engineering and design teams.",
            "skills": ["Product Strategy", "Agile", "User Research", "Roadmapping"]
        },
        {
            "title": "UX Designer",
            "status": "Draft",
            "status_color": "#f59e0b",
            "department": "Design",
            "location": "New York, NY",
            "salary": "$90,000 - $120,000",
            "applicants": 0,
            "date": "Draft created 3 days ago",
            "description": "Looking for a talented UX designer to create intuitive and engaging user experiences for our products.",
            "skills": ["UI/UX", "Figma", "User Testing", "Wireframing"]
        },
        {
            "title": "Data Scientist",
            "status": "Active",
            "status_color": "#10b981",
            "department": "Data",
            "location": "Boston, MA",
            "salary": "$115,000 - $145,000",
            "applicants": 12,
            "date": "Posted 3 weeks ago",
            "description": "Join our data science team to build machine learning models and extract insights from large datasets.",
            "skills": ["Python", "Machine Learning", "SQL", "Data Visualization"]
        },
        {
            "title": "Marketing Specialist",
            "status": "Draft",
            "status_color": "#f59e0b",
            "department": "Marketing",
            "location": "Chicago, IL",
            "salary": "$70,000 - $90,000",
            "applicants": 0,
            "date": "Draft created 1 day ago",
            "description": "Seeking a marketing specialist to develop and execute marketing campaigns across various channels.",
            "skills": ["Digital Marketing", "Content Creation", "Analytics", "Social Media"]
        }
    ]
    
    # Display job positions in a grid
    col1, col2 = st.columns(2)
    
    for i, job in enumerate(job_positions):
        # Create skill badges
        skill_badges = ""
        for skill in job["skills"]:
            skill_badges += f"""
            <span style="background-color: #1f2937; color: #9ca3af; padding: 4px 8px; 
            border-radius: 4px; font-size: 0.8em; margin-right: 5px; margin-bottom: 5px; display: inline-block;">
                {skill}
            </span>
            """
        
        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div class="card" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div>
                        <h3 style="color: white; margin: 0;">{job["title"]}</h3>
                        <p style="color: #9ca3af; margin: 5px 0 0 0; font-size: 0.9em;">
                            {job["department"]} • {job["location"]}
                        </p>
                    </div>
                    <span style="background-color: {job["status_color"]}; color: white; 
                    padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">
                        {job["status"]}
                    </span>
                </div>
                
                <p style="color: white; margin: 10px 0; font-size: 0.9em;">{job["salary"]}</p>
                
                <p style="color: #9ca3af; margin: 10px 0; font-size: 0.9em;">
                    {job["applicants"]} applicants • {job["date"]}
                </p>
                
                <p style="color: #d1d5db; margin: 15px 0; font-size: 0.9em; line-height: 1.5;">
                    {job["description"]}
                </p>
                
                <div style="margin: 15px 0;">
                    {skill_badges}
                </div>
                
                <div style="display: flex; justify-content: flex-end; margin-top: 15px;">
                    <button style="background-color: #374151; color: white; border: none; padding: 6px 12px; 
                    border-radius: 4px; margin-right: 10px; cursor: pointer; font-size: 0.9em;">
                        Edit
                    </button>
                    <button style="background-color: #ef4444; color: white; border: none; padding: 6px 12px; 
                    border-radius: 4px; cursor: pointer; font-size: 0.9em;">
                        Delete
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Create Job Modal
    if st.session_state.show_create_job_modal:
        with st.container():
            st.markdown("""
            <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 0, 0, 0.5); 
            z-index: 1000; display: flex; justify-content: center; align-items: center;">
                <div style="background-color: #1f2937; border-radius: 8px; width: 600px; max-width: 90%; 
                padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="color: white; margin: 0;">Create New Job</h2>
                        <button id="close-modal" style="background: none; border: none; color: #9ca3af; 
                        font-size: 1.5em; cursor: pointer;">×</button>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #9ca3af; margin-bottom: 5px; font-size: 0.9em;">
                            JOB TITLE
                        </label>
                        <input type="text" placeholder="e.g. Senior Software Engineer" 
                        style="width: 100%; padding: 8px; background-color: #374151; border: 1px solid #4b5563; 
                        border-radius: 4px; color: white;">
                    </div>
                    
                    <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                        <div style="flex: 1;">
                            <label style="display: block; color: #9ca3af; margin-bottom: 5px; font-size: 0.9em;">
                                DEPARTMENT
                            </label>
                            <input type="text" placeholder="e.g. Engineering" 
                            style="width: 100%; padding: 8px; background-color: #374151; border: 1px solid #4b5563; 
                            border-radius: 4px; color: white;">
                        </div>
                        <div style="flex: 1;">
                            <label style="display: block; color: #9ca3af; margin-bottom: 5px; font-size: 0.9em;">
                                LOCATION
                            </label>
                            <input type="text" placeholder="e.g. San Francisco, CA" 
                            style="width: 100%; padding: 8px; background-color: #374151; border: 1px solid #4b5563; 
                            border-radius: 4px; color: white;">
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #9ca3af; margin-bottom: 5px; font-size: 0.9em;">
                            SALARY RANGE
                        </label>
                        <input type="text" placeholder="e.g. $120,000 - $150,000" 
                        style="width: 100%; padding: 8px; background-color: #374151; border: 1px solid #4b5563; 
                        border-radius: 4px; color: white;">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #9ca3af; margin-bottom: 5px; font-size: 0.9em;">
                            DESCRIPTION
                        </label>
                        <textarea placeholder="Job description..." rows="4" 
                        style="width: 100%; padding: 8px; background-color: #374151; border: 1px solid #4b5563; 
                        border-radius: 4px; color: white; resize: vertical;"></textarea>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #9ca3af; margin-bottom: 5px; font-size: 0.9em;">
                            REQUIRED SKILLS (comma separated)
                        </label>
                        <input type="text" placeholder="e.g. Python, React, AWS" 
                        style="width: 100%; padding: 8px; background-color: #374151; border: 1px solid #4b5563; 
                        border-radius: 4px; color: white;">
                    </div>
                    
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                        <button style="background-color: #374151; color: white; border: none; padding: 8px 16px; 
                        border-radius: 4px; cursor: pointer;">
                            Save as Draft
                        </button>
                        <button style="background-color: #2563eb; color: white; border: none; padding: 8px 16px; 
                        border-radius: 4px; cursor: pointer;">
                            Publish
                        </button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Close Modal"):
                st.session_state.show_create_job_modal = False
                st.rerun()

def settings_page():
    st.markdown("<h1 style='color: white; font-weight: 600;'>Settings</h1>", unsafe_allow_html=True)
    
    # AI Configuration
    st.markdown("<h2 style='color: white; font-size: 1.3em; margin-top: 20px;'>AI Configuration</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="card">
            <h3 style="color: white; font-size: 1.1em; margin-bottom: 15px;">Matching Weights</h3>
            <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 20px;">
                Adjust how the AI weighs different factors when matching candidates to job positions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.slider("Hard Match", min_value=0, max_value=100, value=70, 
                     help="Weight for exact skill matches")
        
        with col2:
            st.slider("Soft Match", min_value=0, max_value=100, value=30, 
                     help="Weight for related skill matches")
        
        st.slider("Minimum Passing Score", min_value=0, max_value=100, value=60, 
                 help="Minimum score required for a candidate to be considered")
        
        st.slider("Auto-Approve Threshold", min_value=0, max_value=100, value=85, 
                 help="Score threshold for automatic candidate approval")
    
    # File Handling
    st.markdown("<h2 style='color: white; font-size: 1.3em; margin-top: 30px;'>File Handling</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="card">
            <h3 style="color: white; font-size: 1.1em; margin-bottom: 15px;">Document Processing</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Max File Size (MB)", min_value=1, max_value=50, value=10)
            
            st.multiselect("Allowed Resume Formats", 
                          ["PDF", "DOCX", "DOC", "TXT", "RTF"], 
                          default=["PDF", "DOCX"])
        
        with col2:
            st.toggle("Auto-Delete After Processing", value=False)
            st.toggle("Store Original Files", value=True)
            st.toggle("Extract Contact Information", value=True)
    
    # Notifications
    st.markdown("<h2 style='color: white; font-size: 1.3em; margin-top: 30px;'>Notifications</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="card">
            <h3 style="color: white; font-size: 1.1em; margin-bottom: 15px;">Alert Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.toggle("Email Notifications", value=True)
            st.toggle("In-App Notifications", value=True)
        
        with col2:
            st.toggle("New Candidate Alerts", value=True)
            st.toggle("High Match Alerts", value=True)
    
    # Branding & Security
    st.markdown("<h2 style='color: white; font-size: 1.3em; margin-top: 30px;'>Branding & Security</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="card">
                <h3 style="color: white; font-size: 1.1em; margin-bottom: 15px;">Company Branding</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.text_input("Company Name", value="ResumeAI")
            st.text_input("Logo URL", value="https://example.com/logo.png")
            
            st.color_picker("Primary Color", value="#2563eb")
            st.color_picker("Secondary Color", value="#10b981")
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="card">
                <h3 style="color: white; font-size: 1.1em; margin-bottom: 15px;">Security Settings</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.toggle("Two-Factor Authentication", value=False)
            st.toggle("Session Timeout", value=True)
            st.select_slider("Session Duration", options=["30 min", "1 hour", "4 hours", "8 hours"], value="4 hours")
            
            st.text_input("API Key", type="password", value="••••••••••••••••")
    
    # Save Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col2:
        st.button("Reset Defaults", use_container_width=True)
    
    with col3:
        st.button("Save Changes", type="primary", use_container_width=True)

def match_details_modal():
    if st.session_state.modal_data:
        with st.expander("Match Details", expanded=True):
            data = st.session_state.modal_data
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.metric("Final Score", f"{data['final_score']}%")
                st.subheader(data['verdict'], anchor=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.container(border=True):
                    st.subheader(f"✅ Matched Skills ({len(data['breakdown']['matched_skills'])})", anchor=False)
                    for skill in data['breakdown']['matched_skills']:
                        st.write(f"- {skill}")
            
            with col2:
                with st.container(border=True):
                    st.subheader(f"❌ Missing Skills ({len(data['breakdown']['missing_skills'])})", anchor=False)
                    for skill in data['breakdown']['missing_skills']:
                        st.write(f"- {skill}")

def evaluations_page():
    st.markdown("<h1 style='color: white; font-weight: 600;'>Evaluations</h1>", unsafe_allow_html=True)
    
    # Search and filter header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.text_input("Search candidates...", placeholder="Search by name, skills, or position", label_visibility="collapsed")
    
    with col2:
        st.selectbox("Filter", ["All Matches", "High Match", "Medium Match", "Low Match"], label_visibility="collapsed")
    
    with col3:
        st.button("Export", use_container_width=True)
    
    # Job selection
    st.markdown("<br><p style='color: #9ca3af; margin-bottom: 10px;'>SELECT JOB POSITION</p>", unsafe_allow_html=True)
    
    # Mock job positions
    job_positions = ["", "Senior Software Engineer", "Product Manager", "UX Designer", "Data Scientist", "Marketing Specialist"]
    
    selected_job = st.selectbox(
        label="Select a job position to view candidates",
        options=job_positions,
        key="eval_job_select",
        label_visibility="collapsed"
    )
    
    if not selected_job:
        # Empty state
        st.markdown("""
        <div style="border-radius: 8px; padding: 40px 20px; margin-top: 30px;
        text-align: center; background-color: #1f2937;">
            <div style="color: #6b7280; font-size: 3em; margin-bottom: 10px;">🔍</div>
            <h3 style="color: white; margin-bottom: 10px;">No Evaluations Found</h3>
            <p style="color: #9ca3af;">Select a job position to see candidate evaluations</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show candidates for selected job
        st.markdown(f"""
        <div style="margin-top: 20px;">
            <h3 style="color: white; margin-bottom: 15px;">Candidates for {selected_job}</h3>
            <p style="color: #9ca3af; margin-bottom: 20px;">Showing 5 candidates ranked by match score</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Candidate cards
        candidates = [
            {
                "name": "Alex Johnson",
                "match": 95,
                "experience": "5 years",
                "skills": ["Python", "React", "AWS", "Machine Learning"],
                "education": "M.S. Computer Science, Stanford University"
            },
            {
                "name": "Sarah Williams",
                "match": 87,
                "experience": "4 years",
                "skills": ["JavaScript", "React", "Node.js", "UI/UX"],
                "education": "B.S. Computer Science, MIT"
            },
            {
                "name": "Michael Chen",
                "match": 82,
                "experience": "6 years",
                "skills": ["Java", "Spring", "Kubernetes", "Microservices"],
                "education": "M.S. Software Engineering, UC Berkeley"
            },
            {
                "name": "Emily Rodriguez",
                "match": 78,
                "experience": "3 years",
                "skills": ["Python", "Django", "PostgreSQL", "Docker"],
                "education": "B.S. Information Systems, NYU"
            },
            {
                "name": "David Kim",
                "match": 72,
                "experience": "4 years",
                "skills": ["C#", ".NET", "Azure", "SQL Server"],
                "education": "B.S. Computer Engineering, Georgia Tech"
            }
        ]
        
        for candidate in candidates:
            # Determine match color based on score
            if candidate["match"] >= 85:
                match_color = "#10b981"  # Green for high match
            elif candidate["match"] >= 75:
                match_color = "#f59e0b"  # Yellow for medium match
            else:
                match_color = "#6b7280"  # Gray for low match
            
            # Create skill badges
            skill_badges = ""
            for skill in candidate["skills"]:
                skill_badges += f"""
                <span style="background-color: #1f2937; color: #9ca3af; padding: 4px 8px; 
                border-radius: 4px; font-size: 0.8em; margin-right: 5px;">{skill}</span>
                """
            
            st.markdown(f"""
            <div class="card" style="margin-bottom: 15px; cursor: pointer;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: #1f2937; color: white; width: 40px; height: 40px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        margin-right: 15px; font-weight: bold;">
                            {candidate["name"][0]}
                        </div>
                        <div>
                            <h4 style="color: white; margin: 0;">{candidate["name"]}</h4>
                            <p style="color: #9ca3af; margin: 5px 0 0 0; font-size: 0.8em;">
                                {candidate["experience"]} • {candidate["education"]}
                            </p>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="background-color: rgba(37, 99, 235, 0.1); padding: 8px 12px; 
                        border-radius: 8px; display: inline-block;">
                            <span style="color: {match_color}; font-size: 1.2em; font-weight: bold;">
                                {candidate["match"]}%
                            </span>
                        </div>
                    </div>
                </div>
                <div style="margin-top: 15px;">
                    {skill_badges}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a button to view details
            if st.button(f"View Details", key=f"view_{candidate['name']}"):
                st.session_state.selected_candidate = candidate
                st.session_state.show_candidate_details = True
    
    with col1:
        with st.container(border=True):
            st.subheader("Job Positions", anchor=False)
            
            uploaded_jd = st.file_uploader("Upload New JD", type=["pdf", "docx"], key="jd_uploader")
            if uploaded_jd:
                handle_file_upload(uploaded_jd, 'jd')
            
            if not st.session_state.job_positions:
                st.info("No job positions found. Upload a JD to begin.")
            else:
                for jd in st.session_state.job_positions:
                    job_title = jd.get('job_title') or jd.get('file_name')
                    if st.button(f"{job_title}\n{jd.get('file_name')}", 
                                key=f"jd_{jd.get('id')}", 
                                use_container_width=True,
                                type="primary" if st.session_state.selected_jd_id == jd.get('id') else "secondary"):
                        select_job_position(jd.get('id'))
    
    with col2:
        with st.container(border=True):
            st.subheader("Ranked Candidates", anchor=False)
            
            uploaded_resume = st.file_uploader("Upload Resume for this JD", 
                                            type=["pdf", "docx"], 
                                            key="resume_uploader",
                                            disabled=not st.session_state.selected_jd_id)
            if uploaded_resume:
                handle_file_upload(uploaded_resume, 'resume')
            
            if not st.session_state.selected_jd_id:
                st.info("Select a job to see results.")
            elif not st.session_state.ranked_candidates:
                st.info("No candidates found. Upload a resume to begin analysis.")
            else:
                for candidate in st.session_state.ranked_candidates:
                    col_name, col_score, col_button = st.columns([2, 1, 1])
                    with col_name:
                        st.write(candidate.get('file_name'))
                    with col_score:
                        st.metric("Score", f"{candidate.get('score')}%", label_visibility="collapsed")
                    with col_button:
                        if st.button("View Details", key=f"view_{candidate.get('resume_id')}"):
                            fetch_match_details(candidate.get('resume_id'), st.session_state.selected_jd_id)
                    st.divider()
            
            match_details_modal()

def upload_page():
    st.markdown("<h1 style='color: white; font-weight: 600;'>Upload Resume</h1>", unsafe_allow_html=True)
    
    # Job selection dropdown
    st.markdown("<p style='color: #9ca3af; margin-bottom: 10px;'>SELECT JOB POSITION</p>", unsafe_allow_html=True)
    
    # Use job positions from session state
    if "job_positions" not in st.session_state:
        st.session_state.job_positions = [
            {"id": "1", "title": "Senior Software Engineer"},
            {"id": "2", "title": "Product Manager"},
            {"id": "3", "title": "UX Designer"},
            {"id": "4", "title": "Data Scientist"},
            {"id": "5", "title": "Marketing Specialist"}
        ]
    
    # Create options list with empty first option
    job_options = [""]
    job_options.extend([job["title"] for job in st.session_state.job_positions])
    
    # Create a styled dropdown
    selected_job = st.selectbox(
        label="Select a job position",
        options=job_options,
        label_visibility="collapsed",
        key="upload_job_selection"
    )
    
    # Store selected job in session state
    if selected_job:
        for job in st.session_state.job_positions:
            if job["title"] == selected_job:
                st.session_state.selected_job = job
                break
    
    # File upload area - disabled until job is selected
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af; margin-bottom: 10px;'>UPLOAD RESUME</p>", unsafe_allow_html=True)
    
    if not selected_job:
        # Disabled upload area
        st.markdown("""
        <div style="border: 2px dashed #4b5563; border-radius: 8px; padding: 40px 20px; 
        text-align: center; background-color: #1f2937; opacity: 0.6; cursor: not-allowed;">
            <div style="color: #9ca3af; font-size: 3em; margin-bottom: 10px;">📄</div>
            <h3 style="color: #9ca3af; margin-bottom: 10px;">Upload Resume</h3>
            <p style="color: #6b7280;">Please select a job position first</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Disabled analyze button
        st.button("Analyze", disabled=True, use_container_width=True)
    else:
        # Active upload area
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF, DOCX)",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key="resume_uploader"
        )
        
        if uploaded_file is not None:
            # Show file details
            st.markdown(f"""
            <div class="card" style="margin-top: 20px;">
                <div style="display: flex; align-items: center;">
                    <div style="background-color: rgba(37, 99, 235, 0.2); padding: 10px; border-radius: 8px; margin-right: 15px;">
                        <span style="color: #2563eb; font-size: 1.5em;">📄</span>
                    </div>
                    <div>
                        <h4 style="color: white; margin: 0;">{uploaded_file.name}</h4>
                        <p style="color: #9ca3af; margin: 5px 0 0 0; font-size: 0.8em;">
                            {round(uploaded_file.size/1024, 1)} KB • Ready to analyze
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Store the uploaded file in session state
            if "uploaded_files" not in st.session_state:
                st.session_state.uploaded_files = []
            
            # Check if file is already in uploaded_files
            file_exists = False
            for file in st.session_state.uploaded_files:
                if file.get("name") == uploaded_file.name:
                    file_exists = True
                    break
            
            if not file_exists:
                # Add file to session state
                file_info = {
                    "name": uploaded_file.name,
                    "size": uploaded_file.size,
                    "job_id": st.session_state.selected_job["id"],
                    "job_title": st.session_state.selected_job["title"],
                    "status": "pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.uploaded_files.append(file_info)
            
            # Analyze button
            if st.button("Analyze Resume", type="primary", use_container_width=True):
                # Simulate API call with progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(101):
                    # Update progress bar
                    progress_bar.progress(i)
                    
                    # Update status text based on progress
                    if i < 30:
                        status_text.text("Extracting resume data...")
                    elif i < 60:
                        status_text.text("Analyzing skills and experience...")
                    elif i < 90:
                        status_text.text("Matching with job requirements...")
                    else:
                        status_text.text("Finalizing evaluation...")
                    
                    # Simulate processing time
                    time.sleep(0.02)
                
                # Update file status in session state
                for file in st.session_state.uploaded_files:
                    if file.get("name") == uploaded_file.name:
                        file["status"] = "completed"
                        break
                
                # Success message
                st.success("Resume analysis complete!")
                
                # Add candidate to session state
                if "candidates" not in st.session_state:
                    st.session_state.candidates = []
                
                # Create a new candidate with mock data
                new_candidate = {
                    "id": str(len(st.session_state.candidates) + 1),
                    "name": uploaded_file.name.split('.')[0],
                    "job_id": st.session_state.selected_job["id"],
                    "job_title": st.session_state.selected_job["title"],
                    "match_score": random.randint(70, 95),
                    "status": "New",
                    "resume_file": uploaded_file.name
                }
                
                st.session_state.candidates.append(new_candidate)
                
                # Show view results button
                if st.button("View Results", type="primary"):
                    st.session_state.current_page = "evaluations"
                    st.rerun()
        else:
            # Active upload area with no file
            st.markdown("""
            <div style="border: 2px dashed #4b5563; border-radius: 8px; padding: 40px 20px; 
            text-align: center; background-color: #1f2937; cursor: pointer;">
                <div style="color: #2563eb; font-size: 3em; margin-bottom: 10px;">📄</div>
                <h3 style="color: white; margin-bottom: 10px;">Upload Resume</h3>
                <p style="color: #9ca3af;">Drag and drop your file here or click to browse</p>
                <p style="color: #6b7280; font-size: 0.8em; margin-top: 15px;">Supported formats: PDF, DOCX</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Disabled analyze button
            st.button("Analyze", disabled=True, use_container_width=True)
    
    # Stats section
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 5px;">Total Uploaded</p>
                    <h2 style="color: white; margin: 0;">42</h2>
                </div>
                <div style="background-color: rgba(37, 99, 235, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="color: #2563eb; font-size: 1.2em;">📄</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 5px;">Completed</p>
                    <h2 style="color: white; margin: 0;">38</h2>
                </div>
                <div style="background-color: rgba(16, 185, 129, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="color: #10b981; font-size: 1.2em;">✓</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <p style="color: #9ca3af; font-size: 0.9em; margin-bottom: 5px;">Processing</p>
                    <h2 style="color: white; margin: 0;">4</h2>
                </div>
                <div style="background-color: rgba(245, 158, 11, 0.2); padding: 8px; border-radius: 8px;">
                    <span style="color: #f59e0b; font-size: 1.2em;">⟳</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Main App Logic ---
def main():
    # Initialize session state variables if they don't exist
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    if "job_positions" not in st.session_state:
        st.session_state.job_positions = [
            {
                "id": "job1",
                "title": "Senior Software Engineer",
                "status": "Active",
                "status_color": "#10b981",
                "department": "Engineering",
                "location": "San Francisco, CA",
                "salary": "$120,000 - $150,000",
                "applicants": 24,
                "date": "Posted 2 weeks ago",
                "description": "We're looking for a senior software engineer to join our team and help build our next-generation products.",
                "skills": ["Python", "React", "AWS", "Docker"]
            },
            {
                "id": "job2",
                "title": "Product Manager",
                "status": "Active",
                "status_color": "#10b981",
                "department": "Product",
                "location": "Remote",
                "salary": "$110,000 - $140,000",
                "applicants": 18,
                "date": "Posted 1 week ago",
                "description": "Seeking a product manager to lead our product development process.",
                "skills": ["Product Strategy", "Agile", "User Research", "Roadmapping"]
            },
            {
                "id": "job3",
                "title": "UX Designer",
                "status": "Draft",
                "status_color": "#f59e0b",
                "department": "Design",
                "location": "New York, NY",
                "salary": "$90,000 - $120,000",
                "applicants": 0,
                "date": "Draft created 3 days ago",
                "description": "Looking for a talented UX designer to create intuitive user experiences.",
                "skills": ["UI/UX", "Figma", "User Testing", "Wireframing"]
            }
        ]
    
    if "candidates" not in st.session_state:
        st.session_state.candidates = [
            {
                "id": "cand1",
                "name": "Alex Johnson",
                "job_id": "job1",
                "job_title": "Senior Software Engineer",
                "match": 95,
                "experience": "5 years",
                "skills": ["Python", "React", "AWS", "Machine Learning"],
                "education": "M.S. Computer Science, Stanford University",
                "status": "Completed"
            },
            {
                "id": "cand2",
                "name": "Sarah Williams",
                "job_id": "job1",
                "job_title": "Senior Software Engineer",
                "match": 87,
                "experience": "4 years",
                "skills": ["JavaScript", "React", "Node.js", "UI/UX"],
                "education": "B.S. Computer Science, MIT",
                "status": "Completed"
            },
            {
                "id": "cand3",
                "name": "Michael Chen",
                "job_id": "job2",
                "job_title": "Product Manager",
                "match": 82,
                "experience": "6 years",
                "skills": ["Product Strategy", "Agile", "User Research"],
                "education": "MBA, Harvard Business School",
                "status": "Completed"
            }
        ]
        
    if "backend_error" not in st.session_state:
        st.session_state.backend_error = None
    
    if "show_create_job_modal" not in st.session_state:
        st.session_state.show_create_job_modal = False
        
    if "show_upload_jd" not in st.session_state:
        st.session_state.show_upload_jd = False
        
    if "show_candidate_details" not in st.session_state:
        st.session_state.show_candidate_details = False
        
    if "selected_candidate" not in st.session_state:
        st.session_state.selected_candidate = None
    
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "total_resumes": 45,
            "matched_candidates": 28,
            "active_jobs": 5,
            "success_rate": 62
        }
    
    if "recent_evaluations" not in st.session_state:
        st.session_state.recent_evaluations = [
            {"name": "John Doe", "position": "Software Engineer", "match": 92, "date": "2 hours ago"},
            {"name": "Jane Smith", "position": "Product Manager", "match": 85, "date": "Yesterday"},
            {"name": "Mike Johnson", "position": "Data Scientist", "match": 78, "date": "2 days ago"}
        ]
        
    # Mock job positions for selection
    if "job_positions" not in st.session_state:
        st.session_state.job_positions = [
            {"id": 1, "title": "Senior Software Engineer", "department": "Engineering"},
            {"id": 2, "title": "Product Manager", "department": "Product"},
            {"id": 3, "title": "UX Designer", "department": "Design"},
            {"id": 4, "title": "Data Scientist", "department": "Data"},
            {"id": 5, "title": "Marketing Specialist", "department": "Marketing"}
        ]
    
    # Mock candidates data
    if "all_candidates" not in st.session_state:
        st.session_state.all_candidates = [
            {
                "id": 1,
                "name": "John Doe",
                "position": "Senior Software Engineer",
                "job_id": 1,
                "match": 92,
                "skills": ["Python", "React", "AWS", "Docker"],
                "experience": "8 years",
                "education": "MS Computer Science",
                "contact": "john.doe@example.com",
                "resume_url": "uploads/resume1.pdf"
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "position": "Product Manager",
                "job_id": 2,
                "match": 85,
                "skills": ["Product Strategy", "Agile", "User Research", "Roadmapping"],
                "experience": "6 years",
                "education": "MBA",
                "contact": "jane.smith@example.com",
                "resume_url": "uploads/resume2.pdf"
            },
            {
                "id": 3,
                "name": "Mike Johnson",
                "position": "Data Scientist",
                "job_id": 4,
                "match": 78,
                "skills": ["Python", "Machine Learning", "SQL", "Data Visualization"],
                "experience": "5 years",
                "education": "PhD Statistics",
                "contact": "mike.johnson@example.com",
                "resume_url": "uploads/resume3.pdf"
            },
            {
                "id": 4,
                "name": "Sarah Williams",
                "position": "UX Designer",
                "job_id": 3,
                "match": 88,
                "skills": ["UI/UX", "Figma", "User Testing", "Wireframing"],
                "experience": "4 years",
                "education": "BFA Design",
                "contact": "sarah.williams@example.com",
                "resume_url": "uploads/resume4.pdf"
            },
            {
                "id": 5,
                "name": "David Brown",
                "position": "Senior Software Engineer",
                "job_id": 1,
                "match": 75,
                "skills": ["Java", "Spring", "Kubernetes", "Microservices"],
                "experience": "10 years",
                "education": "BS Computer Science",
                "contact": "david.brown@example.com",
                "resume_url": "uploads/resume5.pdf"
            }
        ]
    
    # Render sidebar
    sidebar()
    
    # Render main content
    if st.session_state.backend_error and not st.session_state.job_positions:
        error_display()
    else:
        if st.session_state.current_page == "dashboard":
            dashboard_page()
        elif st.session_state.current_page == "upload":
            upload_page()
        elif st.session_state.current_page == "evaluations":
            evaluations_page()
        elif st.session_state.current_page == "positions":
            positions_page()
        elif st.session_state.current_page == "settings":
            settings_page()

# --- Run the app ---
if __name__ == "__main__":
    main()

