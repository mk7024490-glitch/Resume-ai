# AI Resume-JD Matcher - Streamlit Frontend

A comprehensive Streamlit frontend for the AI-powered Resume and Job Description matching system.

## Features

### 🎯 Core Functionality
- **Resume Upload & Analysis**: Upload PDF/DOCX resumes for AI-powered skill extraction
- **Job Description Analysis**: Process job descriptions to extract requirements and qualifications
- **Advanced Matching**: Get detailed match scores between resumes and job descriptions
- **Candidate Ranking**: Automatically rank candidates for specific job descriptions
- **Interactive Dashboard**: Visual overview of all matching activities

### 🤖 AI-Powered Features
- **Intelligent Parsing**: Uses Google Gemini LLM for structured data extraction
- **Semantic Matching**: Combines keyword matching with AI semantic similarity
- **Skill Recognition**: Automatically identifies technical skills and qualifications
- **Match Scoring**: Provides detailed breakdown of match scores with explanations

### 📊 Analytics & Visualization
- **Interactive Charts**: Plotly-powered visualizations for match distributions
- **Skills Analysis**: Visual breakdown of matched vs missing skills
- **Score Trends**: Track matching performance over time
- **Candidate Insights**: Comprehensive candidate ranking and analysis

## Installation & Setup

### Prerequisites
1. **Flask Backend**: Ensure the Flask backend (`app.py`) is running on `localhost:5000`
2. **Python Environment**: Python 3.8+ recommended

### Installation Steps

1. **Install Dependencies**:
   \`\`\`bash
   pip install -r requirements_streamlit.txt
   \`\`\`

2. **Start the Streamlit App**:
   \`\`\`bash
   streamlit run streamlit_app.py
   \`\`\`

3. **Access the Application**:
   - Open your browser to `http://localhost:8501`
   - The app will automatically check backend connectivity

## Usage Guide

### 1. Dashboard Overview
- View system metrics and recent activity
- Quick access to all major features
- System status monitoring

### 2. Upload Resume
- Select PDF or DOCX resume files
- AI extracts skills and qualifications automatically
- View extracted skills with visual tags

### 3. Upload Job Description
- Process job description files
- Extract job title, must-have skills, and qualifications
- Organized display of requirements

### 4. Advanced Matching
- **Find Candidates**: Enter JD ID to get ranked candidate list
- **Detailed Analysis**: Get comprehensive match breakdown between specific resume-JD pairs
- **Visual Insights**: Interactive charts showing match distributions and skill analysis

### 5. Analytics
- Comprehensive insights and trends
- Skills demand analysis
- Historical matching data

## API Integration

The Streamlit app integrates with the Flask backend through these endpoints:

- `POST /analyze-resume` - Resume analysis and skill extraction
- `POST /analyze-jd` - Job description analysis
- `GET /matches-for-jd/<jd_id>` - Get ranked candidates for a JD
- `GET /advanced-match/<resume_id>/<jd_id>` - Detailed match analysis

## Technical Features

### 🎨 UI/UX
- **Responsive Design**: Works on desktop and mobile devices
- **Custom Styling**: Professional color scheme and typography
- **Interactive Elements**: Buttons, metrics, and visual feedback
- **Error Handling**: Comprehensive error messages and status indicators

### 📊 Data Visualization
- **Plotly Integration**: Interactive charts and graphs
- **Real-time Updates**: Dynamic content based on backend responses
- **Score Visualization**: Color-coded match scores and progress indicators

### 🔧 System Integration
- **Backend Health Monitoring**: Automatic connectivity checks
- **Error Recovery**: Graceful handling of backend unavailability
- **Session Management**: Maintains state across page navigation

## Troubleshooting

### Common Issues

1. **Backend Connection Error**:
   - Ensure Flask app is running: `python app.py`
   - Check if port 5000 is available
   - Verify backend URL in `BACKEND_URL` variable

2. **File Upload Issues**:
   - Ensure files are PDF or DOCX format
   - Check file size limits
   - Verify backend file processing capabilities

3. **Analysis Errors**:
   - Check if all required environment variables are set in backend
   - Verify Supabase and Gemini API configurations
   - Review backend logs for detailed error messages

### Performance Tips

- **Large Files**: Processing large documents may take longer
- **Concurrent Users**: Backend handles multiple requests but may be slower
- **Cache Management**: Streamlit caches some operations for better performance

## Development

### Adding New Features

1. **New Pages**: Add new functions and update the navigation selectbox
2. **API Endpoints**: Add new request functions following existing patterns
3. **Visualizations**: Use Plotly for consistent chart styling
4. **Styling**: Update the CSS section for custom styling

### Code Structure

- `main()`: Main application entry point and navigation
- `*_page()`: Individual page functions
- `analyze_*()`: Backend API integration functions
- `check_backend_health()`: System monitoring

## Future Enhancements

- **Batch Processing**: Upload multiple files at once
- **Export Features**: Download match reports as PDF/Excel
- **User Authentication**: Multi-user support with profiles
- **Advanced Analytics**: Machine learning insights and predictions
- **Real-time Notifications**: Live updates for long-running processes
