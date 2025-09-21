import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Configure Streamlit page
st.set_page_config(
    page_title="ResumeAI - AI-Powered Hiring",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API configuration
BACKEND_URL = "http://localhost:5000"

st.markdown("""
<style>
    /* Dark theme styling */
    .stApp {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1a1a;
        border-right: 1px solid #333;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #0f0f0f;
    }
    
    /* Custom metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
        margin: 0;
    }
    
    .metric-label {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-trend {
        color: #4ade80;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    /* Dashboard header */
    .dashboard-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .dashboard-subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Section cards */
    .section-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
    
    .section-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .section-subtitle {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Upload area styling */
    .upload-area {
        background: #1a1a1a;
        border: 2px dashed #333;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .upload-disabled {
        background: #1a1a1a;
        border: 2px dashed #333;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        margin: 1rem 0;
        opacity: 0.5;
    }
    
    /* Job card styling */
    .job-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
    }
    
    .job-status {
        position: absolute;
        top: 1rem;
        right: 1rem;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-active {
        background-color: #22c55e;
        color: white;
    }
    
    .status-draft {
        background-color: #f59e0b;
        color: white;
    }
    
    .skill-tag {
        background-color: #374151;
        color: #d1d5db;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
        margin: 0.25rem 0.25rem 0.25rem 0;
        display: inline-block;
    }
    
    /* Settings styling */
    .settings-section {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .slider-container {
        margin: 1rem 0;
    }
    
    .file-format-tag {
        background-color: #3b82f6;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
        margin: 0.25rem 0.25rem 0.25rem 0;
        display: inline-block;
    }
    
    /* Quick actions */
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Status indicators */
    .status-connected {
        color: #4ade80;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-disconnected {
        color: #ef4444;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Try again button */
    .try-again-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
    }
    
    /* Error state styling */
    .error-state {
        text-align: center;
        padding: 3rem 0;
        color: #666;
    }
    
    .error-icon {
        width: 48px;
        height: 48px;
        background-color: #dc2626;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        color: white;
        font-size: 1.5rem;
    }
    
    /* Button styling */
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
        margin: 0.25rem;
    }
    
    .secondary-button {
        background: transparent;
        color: #888;
        border: 1px solid #333;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 2rem;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
            <span style="color: white; font-size: 1.5rem; font-weight: bold;">⚡</span>
        </div>
        <div>
            <h1 style="margin: 0; color: white; font-size: 1.5rem;">ResumeAI</h1>
            <p style="margin: 0; color: #888; font-size: 0.9rem;">AI-Powered Hiring</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.markdown("""
    <div style="padding: 1rem 0;">
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
                <span style="color: white; font-size: 1.2rem;">⚡</span>
            </div>
            <div>
                <div style="color: white; font-weight: bold;">ResumeAI</div>
                <div style="color: #888; font-size: 0.8rem;">AI-Powered Hiring</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "",
        ["📊 Dashboard", "📄 Upload Resume", "📋 Evaluations", "💼 Job Positions", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "📄 Upload Resume":
        upload_resume_page()
    elif page == "📋 Evaluations":
        evaluations_page()
    elif page == "💼 Job Positions":
        job_positions_page()
    elif page == "⚙️ Settings":
        settings_page()

def dashboard_page():
    st.markdown('<div class="dashboard-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Welcome back! Here\'s what\'s happening with your resume analysis today.</div>', unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">📄 Total Resumes</div>
            <div class="metric-value">0</div>
            <div class="metric-trend">📈 +12% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">📊 Daily Evaluations</div>
            <div class="metric-value">0</div>
            <div class="metric-trend">📈 +8% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">⭐ Average Score</div>
            <div class="metric-value">0%</div>
            <div class="metric-trend">📈 +3% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">💼 Active Jobs</div>
            <div class="metric-value">1</div>
            <div class="metric-trend">📈 +2 from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">Recent Evaluations</div>
            <div class="section-subtitle">Latest resume analysis results</div>
            <div style="text-align: center; padding: 3rem 0; color: #666;">
                <div style="margin-bottom: 1rem;">Failed to fetch</div>
                <button class="try-again-btn" onclick="window.location.reload()">Try Again</button>
            </div>
            <div style="text-align: right; margin-top: 1rem;">
                <a href="#" style="color: #667eea; text-decoration: none; font-size: 0.9rem;">View All →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">Quick Actions</div>
            <div class="section-subtitle">Common tasks and shortcuts</div>
            <div style="margin: 1rem 0;">
                <button class="quick-action-btn">📤 Upload New Resume</button>
            </div>
            <div style="margin-top: 2rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #888; font-size: 0.9rem;">Processing Queue</span>
                    <span style="color: white; font-size: 0.9rem;">0/10</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #888; font-size: 0.9rem;">Storage Used</span>
                    <span style="color: white; font-size: 0.9rem;">0.0GB/10GB</span>
                </div>
            </div>
            <div style="margin-top: 2rem;">
                <div style="color: white; font-weight: bold; margin-bottom: 1rem;">System Status</div>
                <div class="status-connected">
                    <span style="width: 8px; height: 8px; background-color: #4ade80; border-radius: 50%; display: inline-block;"></span>
                    Backend connected
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def upload_resume_page():
    st.markdown('<div class="dashboard-header">Upload Resumes</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Upload candidate resumes for AI-powered analysis and scoring.</div>', unsafe_allow_html=True)
    
    # Job Position Selection
    st.markdown("""
    <div class="section-card">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="margin-right: 0.5rem;">💼</span>
            <div class="section-title">Select Job Position</div>
        </div>
        <div class="section-subtitle">Choose the position you're hiring for to ensure accurate matching.</div>
    </div>
    """, unsafe_allow_html=True)
    
    job_position = st.selectbox(
        "",
        ["Select a job position..."],
        label_visibility="collapsed"
    )
    
    # Upload Files Section
    st.markdown("""
    <div class="section-card" style="margin-top: 2rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="margin-right: 0.5rem;">📤</span>
            <div class="section-title">Upload Files</div>
        </div>
        <div class="section-subtitle">Drag and drop resume files or click to browse. Supports PDF, DOC, and DOCX files up to 10MB.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload area (disabled state since no job position selected)
    st.markdown("""
    <div class="upload-disabled">
        <div style="margin-bottom: 1rem;">
            <div style="background: #374151; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; color: #9ca3af;">
                📤
            </div>
        </div>
        <div style="color: #9ca3af; font-size: 1.1rem; margin-bottom: 0.5rem;">Select a job position first</div>
        <div style="color: #6b7280; font-size: 0.9rem;">PDF, DOC, DOCX files up to 10MB each</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="margin-right: 0.5rem; color: #3b82f6;">📄</span>
                <div class="metric-label">Total Uploaded</div>
            </div>
            <div class="metric-value">0</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="margin-right: 0.5rem; color: #22c55e;">✅</span>
                <div class="metric-label">Completed</div>
            </div>
            <div class="metric-value">0</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="margin-right: 0.5rem; color: #06b6d4;">⏳</span>
                <div class="metric-label">Processing</div>
            </div>
            <div class="metric-value">0</div>
        </div>
        """, unsafe_allow_html=True)

def upload_jd_page():
    st.header("💼 Upload & Analyze Job Description")
    st.markdown("Upload a job description file (PDF or DOCX) for AI-powered analysis and requirement extraction.")
    
    uploaded_file = st.file_uploader(
        "Choose a job description file",
        type=['pdf', 'docx'],
        help="Supported formats: PDF, DOCX"
    )
    
    if uploaded_file is not None:
        st.success(f"File selected: {uploaded_file.name}")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔍 Analyze Job Description", type="primary"):
                analyze_jd(uploaded_file)
        
        with col2:
            st.info("💡 The AI will extract job title, required skills, and qualifications.")

def evaluations_page():
    st.markdown('<div class="dashboard-header">Evaluations</div>', unsafe_allow_html=True)
    
    # Upload area at top
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <div style="margin-bottom: 1rem;">
            <div style="background: #374151; width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 0 auto; color: #9ca3af;">
                📄
            </div>
        </div>
        <div style="color: #9ca3af; font-size: 1.1rem; margin-bottom: 0.5rem;">Upload Resume Files</div>
        <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem;">Backend server required for file upload and analysis.</div>
        <button class="secondary-button">📁 Choose Files</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Analyze button (disabled)
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <button class="action-button" style="opacity: 0.5; cursor: not-allowed; width: 300px;">
            📊 Analyze & Store (0 files)
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    # Search and filter controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.text_input("🔍", placeholder="Search candidates or positions...", label_visibility="collapsed")
    with col2:
        st.selectbox("All Matches", ["All Matches", "High Match", "Medium Match", "Low Match"], label_visibility="collapsed")
    with col3:
        if st.button("📤 Export", key="export_evaluations"):
            st.info("Export functionality")
    
    # Main content area with error state
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="section-card">
            <div class="error-state">
                <div class="error-icon">!</div>
                <div style="font-size: 1.1rem; margin-bottom: 0.5rem; color: white;">Error Loading Evaluations</div>
                <div style="margin-bottom: 1rem;">Backend server is not running. Please start your Flask backend server.</div>
                <button class="try-again-btn" onclick="window.location.reload()">🔄 Try Again</button>
                <button class="secondary-button" style="margin-left: 0.5rem;">Check Connection</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="section-card">
            <div style="text-align: center; padding: 3rem 0; color: #666;">
                <div style="margin-bottom: 1rem;">
                    <div style="background: #374151; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; color: #9ca3af;">
                        👁️
                    </div>
                </div>
                <div style="font-size: 1.1rem; margin-bottom: 0.5rem; color: white;">Select an Evaluation</div>
                <div>Click on any evaluation to view detailed candidate information and scoring breakdown.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def job_positions_page():
    st.markdown('<div class="dashboard-header">Job Positions</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Manage job postings and track applications for your open positions.</div>', unsafe_allow_html=True)
    
    # Header actions
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("📤 Upload JD", key="upload_jd"):
            st.info("Upload JD functionality")
    with col3:
        if st.button("➕ Create Job", key="create_job"):
            st.info("Create Job functionality")
    
    # Search and filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.text_input("🔍", placeholder="Search jobs or departments...", label_visibility="collapsed")
    with col2:
        st.selectbox("All Departments", ["All Departments", "Engineering", "Data & Analytics", "Design"], label_visibility="collapsed")
    with col3:
        st.selectbox("All Status", ["All Status", "Active", "Draft", "Closed"], label_visibility="collapsed")
    
    # Job cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="job-card">
            <div class="job-status status-active">Active</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Senior Frontend Developer</h3>
            <div style="color: #888; margin-bottom: 1rem; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">🏢</span>
                Engineering
            </div>
            
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">📍</span>
                Remote
            </div>
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">💰</span>
                $120,000 - $150,000
            </div>
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">👥</span>
                24 applicants
            </div>
            <div style="margin-bottom: 1rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">📅</span>
                Created Sep 14, 2025
            </div>
            
            <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 1rem;">
                We're looking for an experienced Frontend Developer to join our growing team. You'll be responsible for building user-facing...
            </p>
            
            <div style="margin-bottom: 1rem;">
                <div style="color: #888; font-size: 0.8rem; margin-bottom: 0.5rem;">Required Skills:</div>
                <span class="skill-tag">React</span>
                <span class="skill-tag">TypeScript</span>
                <span class="skill-tag">Next.js</span>
                <span class="skill-tag">Tailwind CSS</span>
                <span class="skill-tag">+4 more</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <button class="secondary-button">✏️ Edit</button>
                <button class="secondary-button" style="color: #dc2626; border-color: #dc2626;">🗑️</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="job-card">
            <div class="job-status status-active">Active</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">Data Scientist</h3>
            <div style="color: #888; margin-bottom: 1rem; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">🏢</span>
                Data & Analytics
            </div>
            
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">📍</span>
                New York, NY
            </div>
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">💰</span>
                $100,000 - $130,000
            </div>
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">👥</span>
                18 applicants
            </div>
            <div style="margin-bottom: 1rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">📅</span>
                Created Sep 16, 2025
            </div>
            
            <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 1rem;">
                Join our data team to help drive insights and build machine learning models that power our product decisions.
            </p>
            
            <div style="margin-bottom: 1rem;">
                <div style="color: #888; font-size: 0.8rem; margin-bottom: 0.5rem;">Required Skills:</div>
                <span class="skill-tag">Python</span>
                <span class="skill-tag">Machine Learning</span>
                <span class="skill-tag">SQL</span>
                <span class="skill-tag">TensorFlow</span>
                <span class="skill-tag">+4 more</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <button class="secondary-button">✏️ Edit</button>
                <button class="secondary-button" style="color: #dc2626; border-color: #dc2626;">🗑️</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="job-card">
            <div class="job-status status-draft">Draft</div>
            <h3 style="color: white; margin-bottom: 0.5rem;">UX Designer</h3>
            <div style="color: #888; margin-bottom: 1rem; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">🏢</span>
                Design
            </div>
            
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">📍</span>
                San Francisco, CA
            </div>
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">💰</span>
                $80,000 - $110,000
            </div>
            <div style="margin-bottom: 0.5rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">👥</span>
                0 applicants
            </div>
            <div style="margin-bottom: 1rem; color: #888; display: flex; align-items: center;">
                <span style="margin-right: 0.5rem;">📅</span>
                Created Sep 18, 2025
            </div>
            
            <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 1rem;">
                We're seeking a talented UX Designer to create intuitive and engaging user experiences for our products.
            </p>
            
            <div style="margin-bottom: 1rem;">
                <div style="color: #888; font-size: 0.8rem; margin-bottom: 0.5rem;">Required Skills:</div>
                <span class="skill-tag">Figma</span>
                <span class="skill-tag">Sketch</span>
                <span class="skill-tag">Prototyping</span>
                <span class="skill-tag">User Research</span>
                <span class="skill-tag">+3 more</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <button class="secondary-button">✏️ Edit</button>
                <button class="secondary-button" style="color: #dc2626; border-color: #dc2626;">🗑️</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

def settings_page():
    st.markdown('<div class="dashboard-header">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Configure your AI resume analysis system and preferences.</div>', unsafe_allow_html=True)
    
    # Save Changes button in top right
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("💾 Save Changes", key="save_settings"):
            st.success("Settings saved successfully!")
    
    # AI Configuration Section
    st.markdown("""
    <div class="settings-section">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="margin-right: 0.5rem;">🤖</span>
            <div class="section-title">AI Configuration</div>
        </div>
        <div class="section-subtitle">Adjust how the AI evaluates and scores resumes.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hard Match Weight: 40%**")
        st.slider("", 0, 100, 40, key="hard_match", label_visibility="collapsed")
        st.markdown('<div style="color: #888; font-size: 0.8rem; margin-bottom: 1rem;">Weight for exact keyword matches</div>', unsafe_allow_html=True)
        
        st.markdown("**Minimum Passing Score: 50%**")
        st.slider("", 0, 100, 50, key="min_score", label_visibility="collapsed")
        st.markdown('<div style="color: #888; font-size: 0.8rem;">Minimum score to be considered</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Soft Match Weight: 60%**")
        st.slider("", 0, 100, 60, key="soft_match", label_visibility="collapsed")
        st.markdown('<div style="color: #888; font-size: 0.8rem; margin-bottom: 1rem;">Weight for semantic understanding</div>', unsafe_allow_html=True)
        
        st.markdown("**Auto-Approve Threshold: 85%**")
        st.slider("", 0, 100, 85, key="auto_approve", label_visibility="collapsed")
        st.markdown('<div style="color: #888; font-size: 0.8rem;">Score for automatic approval</div>', unsafe_allow_html=True)
    
    # File Handling Section
    st.markdown("""
    <div class="settings-section" style="margin-top: 2rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="margin-right: 0.5rem;">📁</span>
            <div class="section-title">File Handling</div>
        </div>
        <div class="section-subtitle">Configure file upload and processing settings.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Maximum File Size (MB)**")
        st.number_input("", value=10, min_value=1, max_value=100, key="max_file_size", label_visibility="collapsed")
    
    with col2:
        st.markdown("**Data Retention (days)**")
        st.number_input("", value=365, min_value=1, max_value=3650, key="data_retention", label_visibility="collapsed")
    
    st.markdown("**Allowed File Formats**")
    st.markdown("""
    <div style="margin: 1rem 0;">
        <span class="file-format-tag">PDF</span>
        <span class="file-format-tag">DOC</span>
        <span class="file-format-tag">DOCX</span>
        <span class="file-format-tag">TXT</span>
        <span class="file-format-tag">RTF</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Notifications Section
    st.markdown("""
    <div class="settings-section" style="margin-top: 2rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="margin-right: 0.5rem;">🔔</span>
            <div class="section-title">Notifications</div>
        </div>
        <div class="section-subtitle">Configure how you receive updates and alerts.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Email Notifications**")
    st.checkbox("New resume uploads", value=True)
    st.checkbox("Analysis completion", value=True)
    st.checkbox("High-scoring candidates", value=False)

def analyze_resume(uploaded_file):
    """Analyze uploaded resume using the Flask backend"""
    with st.spinner("🤖 Analyzing resume with AI... This may take a moment."):
        try:
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{BACKEND_URL}/analyze-resume", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Resume analyzed successfully!")
                
                # Display results
                st.subheader("📊 Analysis Results")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Resume ID", result.get('resume_id', 'N/A'))
                
                with col2:
                    skills_count = len(result.get('parsed_details', {}).get('skills', []))
                    st.metric("Skills Extracted", skills_count)
                
                # Display extracted skills
                skills = result.get('parsed_details', {}).get('skills', [])
                if skills:
                    st.subheader("🛠️ Extracted Skills")
                    # Create skill tags
                    skills_html = ""
                    for skill in skills:
                        skills_html += f'<span style="background-color: #e1f5fe; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 0.9em;">{skill}</span> '
                    st.markdown(skills_html, unsafe_allow_html=True)
                else:
                    st.warning("No skills were extracted from the resume.")
                    
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                st.error(f"❌ Error analyzing resume: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Please ensure the Flask app is running on localhost:5000")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

def analyze_jd(uploaded_file):
    """Analyze uploaded job description using the Flask backend"""
    with st.spinner("🤖 Analyzing job description with AI... This may take a moment."):
        try:
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{BACKEND_URL}/analyze-jd", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Job description analyzed successfully!")
                
                # Display results
                st.subheader("📊 Analysis Results")
                parsed_details = result.get('parsed_details', {})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("JD ID", result.get('jd_id', 'N/A'))
                
                with col2:
                    total_skills = len(parsed_details.get('must_have_skills', [])) + len(parsed_details.get('good_to_have_skills', []))
                    st.metric("Total Skills Required", total_skills)
                
                # Display job title
                job_title = parsed_details.get('job_title', 'Not specified')
                st.subheader(f"👔 Job Title: {job_title}")
                
                # Display skills in organized sections
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔴 Must-Have Skills")
                    must_have = parsed_details.get('must_have_skills', [])
                    if must_have:
                        for skill in must_have:
                            st.markdown(f"• {skill}")
                    else:
                        st.info("No must-have skills specified")
                
                with col2:
                    st.subheader("🟡 Good-to-Have Skills")
                    good_to_have = parsed_details.get('good_to_have_skills', [])
                    if good_to_have:
                        for skill in good_to_have:
                            st.markdown(f"• {skill}")
                    else:
                        st.info("No good-to-have skills specified")
                
                # Display qualifications
                qualifications = parsed_details.get('qualifications', [])
                if qualifications:
                    st.subheader("🎓 Qualifications")
                    for qual in qualifications:
                        st.markdown(f"• {qual}")
                        
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                st.error(f"❌ Error analyzing job description: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Please ensure the Flask app is running on localhost:5000")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

def advanced_matching_page():
    st.header("🔍 Advanced Resume-JD Matching")
    st.markdown("Get detailed matching analysis between specific resumes and job descriptions.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Select Job Description")
        jd_id = st.text_input("Job Description ID", help="Enter the JD ID from previous analysis")
        
        if jd_id and st.button("🔍 Find Candidates", type="primary"):
            find_candidates_for_jd(jd_id)
    
    with col2:
        st.subheader("🎯 Detailed Match Analysis")
        resume_id = st.text_input("Resume ID", help="Enter the Resume ID")
        jd_id_detail = st.text_input("JD ID for detailed analysis", help="Enter the JD ID")
        
        if resume_id and jd_id_detail and st.button("📊 Get Detailed Analysis"):
            get_detailed_match_analysis(resume_id, jd_id_detail)

def find_candidates_for_jd(jd_id):
    """Find and rank candidates for a specific job description"""
    with st.spinner("🔍 Finding and ranking candidates..."):
        try:
            response = requests.get(f"{BACKEND_URL}/matches-for-jd/{jd_id}")
            
            if response.status_code == 200:
                candidates = response.json()
                
                if candidates:
                    st.success(f"✅ Found {len(candidates)} candidates!")
                    
                    # Create DataFrame for better display
                    df = pd.DataFrame(candidates)
                    df = df.sort_values('score', ascending=False)
                    
                    # Display top candidates
                    st.subheader("🏆 Top Candidates")
                    
                    for idx, candidate in df.head(10).iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{candidate['file_name']}**")
                        
                        with col2:
                            score = candidate['score']
                            color = "green" if score >= 70 else "orange" if score >= 50 else "red"
                            st.markdown(f"<span style='color: {color}; font-weight: bold;'>{score}%</span>", unsafe_allow_html=True)
                        
                        with col3:
                            if st.button(f"Details", key=f"detail_{candidate['resume_id']}"):
                                st.session_state[f"show_details_{candidate['resume_id']}"] = True
                    
                    # Visualization
                    if len(df) > 1:
                        st.subheader("📊 Score Distribution")
                        fig = px.histogram(df, x='score', nbins=10, title="Candidate Score Distribution")
                        fig.update_layout(xaxis_title="Match Score (%)", yaxis_title="Number of Candidates")
                        st.plotly_chart(fig, use_container_width=True)
                        
                else:
                    st.info("No candidates found for this job description.")
                    
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                st.error(f"❌ Error finding candidates: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Please ensure the Flask app is running on localhost:5000")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

def get_detailed_match_analysis(resume_id, jd_id):
    """Get detailed matching analysis between a resume and job description"""
    with st.spinner("📊 Generating detailed match analysis..."):
        try:
            response = requests.get(f"{BACKEND_URL}/advanced-match/{resume_id}/{jd_id}")
            
            if response.status_code == 200:
                analysis = response.json()
                
                st.success("✅ Detailed analysis completed!")
                
                # Overall score and verdict
                col1, col2 = st.columns(2)
                with col1:
                    final_score = analysis['final_score']
                    st.metric("Overall Match Score", f"{final_score}%")
                
                with col2:
                    verdict = analysis['verdict']
                    color = "green" if "Excellent" in verdict else "blue" if "Good" in verdict else "orange" if "Review" in verdict else "red"
                    st.markdown(f"**Verdict:** <span style='color: {color}; font-weight: bold;'>{verdict}</span>", unsafe_allow_html=True)
                
                # Detailed breakdown
                breakdown = analysis['breakdown']
                
                st.subheader("📊 Score Breakdown")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Hard Match Score", f"{breakdown['hard_match_score']}%", help="Based on exact and fuzzy skill matching")
                
                with col2:
                    st.metric("Semantic Match Score", f"{breakdown['semantic_match_score']}%", help="Based on AI semantic similarity")
                
                # Skills analysis
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Matched Skills")
                    matched_skills = breakdown['matched_skills']
                    if matched_skills:
                        for skill in matched_skills:
                            st.markdown(f"• ✅ {skill}")
                    else:
                        st.info("No exact skill matches found")
                
                with col2:
                    st.subheader("❌ Missing Skills")
                    missing_skills = breakdown['missing_skills']
                    if missing_skills:
                        for skill in missing_skills:
                            st.markdown(f"• ❌ {skill}")
                    else:
                        st.success("All required skills are present!")
                
                # Visualization
                if matched_skills or missing_skills:
                    st.subheader("📈 Skills Match Visualization")
                    
                    # Create pie chart
                    matched_count = len(matched_skills)
                    missing_count = len(missing_skills)
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=['Matched Skills', 'Missing Skills'],
                        values=[matched_count, missing_count],
                        hole=.3,
                        marker_colors=['#2E8B57', '#DC143C']
                    )])
                    
                    fig.update_layout(title="Skills Match Overview")
                    st.plotly_chart(fig, use_container_width=True)
                    
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                st.error(f"❌ Error getting detailed analysis: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Please ensure the Flask app is running on localhost:5000")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

def analytics_page():
    st.header("📈 Analytics & Insights")
    st.markdown("Comprehensive analytics and insights from your resume-JD matching data.")
    
    # Placeholder for analytics
    st.info("📊 Analytics features will be populated once you have uploaded resumes and job descriptions.")
    
    # Mock analytics sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Match Score Trends")
        st.info("Track how match scores change over time")
    
    with col2:
        st.subheader("🛠️ Top Skills in Demand")
        st.info("See which skills appear most frequently in job descriptions")
    
    st.subheader("📋 Recent Matches")
    st.info("View your most recent matching analyses")

# Backend health check
def check_backend_health():
    """Check if the Flask backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

# Display backend status in sidebar
with st.sidebar:
    st.markdown("---")
    
    if check_backend_health():
        st.markdown("""
        <div class="status-connected" style="margin-top: 1rem;">
            <span style="width: 8px; height: 8px; background-color: #4ade80; border-radius: 50%; display: inline-block;"></span>
            Backend Connected
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-disconnected" style="margin-top: 1rem;">
            <span style="width: 8px; height: 8px; background-color: #ef4444; border-radius: 50%; display: inline-block;"></span>
            Backend Offline
        </div>
        """, unsafe_allow_html=True)
        st.markdown("Please start the Flask backend:")
        st.code("python app.py", language="bash")

if __name__ == "__main__":
    main()
