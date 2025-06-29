import streamlit as st
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configure Streamlit
st.set_page_config(
    page_title="EduTutor AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .quiz-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    .success-card {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-card {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-card {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'token' not in st.session_state:
    st.session_state.token = None
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def login_user(email, password):
    """Login user via backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.user = data["user"]
            st.session_state.token = data["token"]
            return True, "Login successful!"
        else:
            return False, "Invalid credentials"
            
    except Exception as e:
        return False, f"Error connecting to backend: {e}"

def generate_quiz(topic, difficulty, num_questions):
    """Generate quiz via backend API"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.post(
            f"{BACKEND_URL}/quiz/generate",
            json={
                "topic": topic,
                "difficulty": difficulty,
                "num_questions": num_questions
            },
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error generating quiz: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return None

def submit_quiz(quiz_id, answers, time_spent=0):
    """Submit quiz answers"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.post(
            f"{BACKEND_URL}/quiz/submit",
            json={
                "quiz_id": quiz_id,
                "answers": answers,
                "time_spent": time_spent
            },
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error submitting quiz: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error submitting quiz: {e}")
        return None

def get_student_progress():
    """Get student progress data"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(
            f"{BACKEND_URL}/students/progress",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
            
    except Exception as e:
        st.error(f"Error getting student progress: {e}")
        return []

def get_quiz_history(user_id):
    """Get quiz history for user"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(
            f"{BACKEND_URL}/quiz/history/{user_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"attempts": [], "analytics": {}}
            
    except Exception as e:
        st.error(f"Error getting quiz history: {e}")
        return {"attempts": [], "analytics": {}}

def get_recommendations(user_id):
    """Get adaptive learning recommendations"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(
            f"{BACKEND_URL}/recommendations/{user_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"recommendations": {}, "similar_learners": []}
            
    except Exception as e:
        return {"recommendations": {}, "similar_learners": []}

def create_diagnostic_test(user_id, subjects):
    """Create diagnostic test"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.post(
            f"{BACKEND_URL}/quiz/diagnostic",
            json={"user_id": user_id, "subjects": subjects},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error creating diagnostic test: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error creating diagnostic test: {e}")
        return None

def login_page():
    """Login page"""
    st.markdown('<div class="main-header"><h1>🧠 EduTutor AI</h1><p>Personalized Learning with IBM Granite AI</p></div>', unsafe_allow_html=True)
    
    # Check backend status
    if not check_backend_health():
        st.error("⚠️ Backend is not running. Please start the FastAPI backend first.")
        st.code("cd backend && python main.py")
        return
    
    st.success("✅ Backend is running!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login to Continue")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both email and password")
        
        # Demo credentials
        st.markdown("---")
        st.markdown("### Demo Credentials")
        col_a, col_b = st.columns(2)
        with col_a:
            st.info("**Student Account**\nEmail: student@demo.com\nPassword: password")
        with col_b:
            st.info("**Educator Account**\nEmail: teacher@demo.com\nPassword: password")

def student_dashboard():
    """Student dashboard"""
    st.markdown(f'<div class="main-header"><h1>Welcome back, {st.session_state.user["name"]}!</h1><p>Ready to continue your learning journey?</p></div>', unsafe_allow_html=True)
    
    # Check if diagnostic test is completed
    if not st.session_state.user.get("diagnostic_completed", False):
        st.warning("🎯 Complete your diagnostic assessment to get personalized recommendations!")
        if st.button("Take Diagnostic Test"):
            st.session_state.page = "diagnostic"
            st.rerun()
    
    # Get user recommendations
    recommendations = get_recommendations(st.session_state.user["id"])
    user_recommendations = recommendations.get("recommendations", {})
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Recommended Difficulty", user_recommendations.get("recommended_difficulty", "Medium").title())
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Overall Score", f"{user_recommendations.get('overall_score', 0):.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Focus Areas", len(user_recommendations.get("focus_areas", [])))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Performance", user_recommendations.get("performance_trend", "Stable").title())
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🚀 Quick Actions")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("🧠 Take New Quiz", use_container_width=True):
                st.session_state.page = "quiz"
                st.rerun()
        
        with action_col2:
            if st.button("📊 View Progress", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()
        
        # Recommended learning path
        if user_recommendations.get("learning_path"):
            st.markdown("### 🎯 Your Learning Path")
            for i, step in enumerate(user_recommendations["learning_path"][:3]):
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                st.markdown(f"""
                **{i+1}. {step['topic']}** {priority_color.get(step['priority'], '🔵')}
                - *{step['reason']}*
                - Suggested difficulty: {step['suggested_difficulty']}
                """)
    
    with col2:
        st.markdown("### 💡 Recommendations")
        
        if user_recommendations.get("next_steps"):
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.markdown(f"**Next Steps:**\n{user_recommendations['next_steps']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recommended topics
        if user_recommendations.get("recommended_topics"):
            st.markdown("**Recommended Topics:**")
            for topic in user_recommendations["recommended_topics"][:3]:
                st.markdown(f"• {topic}")
        
        # Similar learners
        similar_learners = recommendations.get("similar_learners", [])
        if similar_learners:
            st.markdown("**Similar Learners:**")
            for learner in similar_learners[:3]:
                st.markdown(f"• User {learner['user_id'][-4:]} ({learner['similarity_score']:.1%} similar)")

def educator_dashboard():
    """Educator dashboard"""
    st.markdown(f'<div class="main-header"><h1>Educator Dashboard</h1><p>Welcome, {st.session_state.user["name"]}!</p></div>', unsafe_allow_html=True)
    
    # Get student progress data
    students_data = get_student_progress()
    
    if not students_data:
        st.info("No student data available yet.")
        return
    
    # Overview metrics
    total_students = len(students_data)
    total_quizzes = sum(student.get("totalQuizzes", 0) for student in students_data)
    avg_score = sum(student.get("averageScore", 0) for student in students_data) / total_students if total_students > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Students", total_students)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Quizzes", total_quizzes)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Average Score", f"{avg_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Today", total_students // 2)  # Mock data
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts and analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Student Performance Distribution")
        
        # Create performance distribution chart
        scores = [student.get("averageScore", 0) for student in students_data]
        if scores:
            fig = px.histogram(
                x=scores,
                nbins=10,
                title="Score Distribution",
                labels={"x": "Average Score", "y": "Number of Students"}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Topic Performance")
        
        # Aggregate topic performance
        topic_scores = {}
        for student in students_data:
            for topic, score in student.get("topicProgress", {}).items():
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(score)
        
        # Calculate averages
        topic_averages = {topic: sum(scores)/len(scores) for topic, scores in topic_scores.items()}
        
        if topic_averages:
            fig = px.bar(
                x=list(topic_averages.keys()),
                y=list(topic_averages.values()),
                title="Average Scores by Topic",
                labels={"x": "Topic", "y": "Average Score"}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Student details table
    st.markdown("### 👥 Student Details")
    
    if students_data:
        df = pd.DataFrame(students_data)
        df = df[["userName", "email", "totalQuizzes", "averageScore", "lastActivity"]]
        df.columns = ["Name", "Email", "Total Quizzes", "Average Score", "Last Activity"]
        df["Average Score"] = df["Average Score"].round(1)
        
        st.dataframe(df, use_container_width=True)

def quiz_page():
    """Quiz taking page"""
    if st.session_state.current_quiz is None:
        # Quiz setup
        st.markdown('<div class="main-header"><h1>🧠 Create Your Quiz</h1><p>Customize your learning experience with AI-generated questions</p></div>', unsafe_allow_html=True)
        
        with st.form("quiz_setup"):
            col1, col2 = st.columns(2)
            
            with col1:
                topic = st.selectbox(
                    "Select Topic",
                    ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "History", "Geography"]
                )
                
                difficulty = st.selectbox(
                    "Difficulty Level",
                    ["easy", "medium", "hard"]
                )
            
            with col2:
                num_questions = st.slider(
                    "Number of Questions",
                    min_value=3,
                    max_value=15,
                    value=5
                )
                
                st.info(f"Estimated time: {num_questions * 1.5:.0f} minutes")
            
            generate_button = st.form_submit_button("🚀 Generate Quiz", use_container_width=True)
            
            if generate_button:
                with st.spinner("Generating your personalized quiz..."):
                    quiz_data = generate_quiz(topic, difficulty, num_questions)
                    
                    if quiz_data:
                        st.session_state.current_quiz = quiz_data
                        st.session_state.quiz_answers = {}
                        st.session_state.current_question = 0
                        st.success("Quiz generated successfully!")
                        st.rerun()
    
    else:
        # Quiz interface
        quiz = st.session_state.current_quiz
        
        # Quiz header
        st.markdown(f'<div class="main-header"><h1>{quiz["title"]}</h1><p>Topic: {quiz["topic"]} • Difficulty: {quiz["difficulty"]}</p></div>', unsafe_allow_html=True)
        
        # Progress bar
        progress = len(st.session_state.quiz_answers) / len(quiz["questions"])
        st.progress(progress)
        st.markdown(f"Progress: {len(st.session_state.quiz_answers)}/{len(quiz['questions'])} questions answered")
        
        # Display questions
        st.markdown("### Questions")
        
        for i, question in enumerate(quiz["questions"]):
            with st.container():
                st.markdown(f'<div class="quiz-card">', unsafe_allow_html=True)
                st.markdown(f"**Question {i+1}:** {question['question']}")
                
                # Answer options
                answer_key = f"q_{i}"
                selected_answer = st.radio(
                    "Select your answer:",
                    options=question["options"],
                    key=answer_key,
                    index=st.session_state.quiz_answers.get(i, None)
                )
                
                # Store answer
                if selected_answer:
                    st.session_state.quiz_answers[i] = question["options"].index(selected_answer)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit quiz
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("❌ Exit Quiz"):
                st.session_state.current_quiz = None
                st.session_state.quiz_answers = {}
                st.rerun()
        
        with col2:
            answered_count = len(st.session_state.quiz_answers)
            total_questions = len(quiz["questions"])
            st.info(f"Answered: {answered_count}/{total_questions}")
        
        with col3:
            if st.button("✅ Submit Quiz", disabled=len(st.session_state.quiz_answers) == 0):
                # Prepare answers array
                answers = []
                for i in range(len(quiz["questions"])):
                    answers.append(st.session_state.quiz_answers.get(i, -1))
                
                with st.spinner("Submitting quiz..."):
                    result = submit_quiz(quiz["id"], answers)
                    
                    if result:
                        st.session_state.quiz_result = result
                        st.session_state.current_quiz = None
                        st.session_state.quiz_answers = {}
                        st.session_state.page = "result"
                        st.rerun()

def quiz_result_page():
    """Quiz result page"""
    if 'quiz_result' not in st.session_state:
        st.error("No quiz result found.")
        return
    
    result = st.session_state.quiz_result
    score = result["score"]
    
    # Result header
    if score >= 80:
        st.markdown('<div class="success-card">', unsafe_allow_html=True)
        st.markdown(f"# 🎉 Excellent! {score}%")
    elif score >= 60:
        st.markdown('<div class="warning-card">', unsafe_allow_html=True)
        st.markdown(f"# 👍 Good Job! {score}%")
    else:
        st.markdown('<div class="error-card">', unsafe_allow_html=True)
        st.markdown(f"# 📚 Keep Practicing! {score}%")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feedback
    if result.get("feedback"):
        st.markdown("### 💬 Personalized Feedback")
        st.info(result["feedback"])
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.page = "quiz"
            if 'quiz_result' in st.session_state:
                del st.session_state.quiz_result
            st.rerun()
    
    with col2:
        if st.button("📊 View History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()
    
    with col3:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

def quiz_history_page():
    """Quiz history page"""
    st.markdown('<div class="main-header"><h1>📊 Quiz History</h1><p>Track your learning progress</p></div>', unsafe_allow_html=True)
    
    # Get quiz history
    history_data = get_quiz_history(st.session_state.user["id"])
    attempts = history_data.get("attempts", [])
    
    if not attempts:
        st.info("No quiz history found. Take your first quiz to see your progress!")
        if st.button("Take Quiz"):
            st.session_state.page = "quiz"
            st.rerun()
        return
    
    # Summary statistics
    total_quizzes = len(attempts)
    avg_score = sum(attempt.score for attempt in attempts) / total_quizzes
    best_score = max(attempt.score for attempt in attempts)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Quizzes", total_quizzes)
    
    with col2:
        st.metric("Average Score", f"{avg_score:.1f}%")
    
    with col3:
        st.metric("Best Score", f"{best_score}%")
    
    # Score trend chart
    if len(attempts) > 1:
        st.markdown("### 📈 Score Trend")
        
        scores = [attempt.score for attempt in attempts]
        dates = [attempt.completed_at for attempt in attempts]
        
        fig = px.line(
            x=dates,
            y=scores,
            title="Score Progress Over Time",
            labels={"x": "Date", "y": "Score (%)"}
        )
        fig.update_traces(mode='markers+lines')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent attempts table
    st.markdown("### 📋 Recent Attempts")
    
    attempts_data = []
    for attempt in attempts[-10:]:  # Last 10 attempts
        attempts_data.append({
            "Date": attempt.completed_at[:10],
            "Score": f"{attempt.score}%",
            "Time Spent": f"{attempt.time_spent}s" if attempt.time_spent else "N/A"
        })
    
    if attempts_data:
        df = pd.DataFrame(attempts_data)
        st.dataframe(df, use_container_width=True)

def diagnostic_test_page():
    """Diagnostic test page"""
    st.markdown('<div class="main-header"><h1>🎯 Diagnostic Assessment</h1><p>Help us understand your current knowledge level</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to your diagnostic assessment!
    
    This test will help us understand your current knowledge level across different subjects.
    Based on your performance, we'll create a personalized learning path just for you.
    
    **What to expect:**
    - Questions from multiple subjects
    - Adaptive difficulty based on your answers
    - Approximately 15-20 minutes to complete
    - Immediate personalized recommendations
    """)
    
    # Subject selection
    st.markdown("### Select subjects to assess:")
    
    subjects = st.multiselect(
        "Choose subjects for your diagnostic test:",
        ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science"],
        default=["Mathematics", "Physics", "Chemistry"]
    )
    
    if len(subjects) < 2:
        st.warning("Please select at least 2 subjects for a comprehensive assessment.")
        return
    
    if st.button("🚀 Start Diagnostic Test", use_container_width=True):
        with st.spinner("Creating your personalized diagnostic test..."):
            diagnostic_quiz = create_diagnostic_test(st.session_state.user["id"], subjects)
            
            if diagnostic_quiz:
                st.session_state.current_quiz = diagnostic_quiz
                st.session_state.quiz_answers = {}
                st.session_state.page = "quiz"
                st.success("Diagnostic test created! Starting now...")
                st.rerun()

def main():
    """Main Streamlit app"""
    
    # Initialize page state
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Check if user is logged in
    if not st.session_state.user:
        login_page()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user['name']}")
        st.markdown(f"Role: {st.session_state.user['role'].title()}")
        
        st.markdown("---")
        
        # Navigation based on role
        if st.session_state.user["role"] == "student":
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            
            if st.button("🧠 Take Quiz", use_container_width=True):
                st.session_state.page = "quiz"
                st.rerun()
            
            if st.button("📊 Quiz History", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()
            
            if not st.session_state.user.get("diagnostic_completed", False):
                if st.button("🎯 Diagnostic Test", use_container_width=True):
                    st.session_state.page = "diagnostic"
                    st.rerun()
        
        else:  # Educator
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            
            if st.button("👥 Students", use_container_width=True):
                st.session_state.page = "students"
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Main content based on current page
    if st.session_state.page == "dashboard":
        if st.session_state.user["role"] == "student":
            student_dashboard()
        else:
            educator_dashboard()
    
    elif st.session_state.page == "quiz":
        quiz_page()
    
    elif st.session_state.page == "result":
        quiz_result_page()
    
    elif st.session_state.page == "history":
        quiz_history_page()
    
    elif st.session_state.page == "diagnostic":
        diagnostic_test_page()
    
    elif st.session_state.page == "students":
        educator_dashboard()  # Same as dashboard for educators

if __name__ == "__main__":
    main()