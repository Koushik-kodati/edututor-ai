import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import gradio as gr
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import requests
import threading
import time

# Import services
from backend.services.watsonx_service import watsonx_service
from backend.services.pinecone_service import pinecone_service
from backend.services.google_classroom_service import google_classroom_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
flask_app = Flask(__name__)
flask_app.secret_key = os.getenv('SECRET_KEY', 'edututor_ai_secret_key_2024')

# Enhanced user database with hashed passwords
users_db = {
    "student@demo.com": {
        "id": "student1",
        "email": "student@demo.com",
        "name": "Demo Student",
        "password": hashlib.sha256("password".encode()).hexdigest(),
        "role": "student",
        "diagnostic_completed": False,
        "created_at": "2024-01-01",
        "last_login": None
    },
    "teacher@demo.com": {
        "id": "teacher1",
        "email": "teacher@demo.com",
        "name": "Demo Teacher",
        "password": hashlib.sha256("password".encode()).hexdigest(),
        "role": "teacher",
        "diagnostic_completed": True,
        "created_at": "2024-01-01",
        "last_login": None
    }
}

quizzes_db = {}
attempts_db = {}

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

# Flask Routes
@flask_app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = users_db.get(email)
        if user and verify_password(password, user['password']):
            # Update last login
            user['last_login'] = datetime.now().isoformat()
            session['user'] = user
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('auth/login.html')

@flask_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        # Validation
        if email in users_db:
            flash('Email already exists. Please use a different email.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        else:
            # Create new user
            user_id = f"{role}_{len(users_db) + 1}"
            new_user = {
                "id": user_id,
                "email": email,
                "name": name,
                "password": hash_password(password),
                "role": role,
                "diagnostic_completed": False,
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
            
            users_db[email] = new_user
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('auth/signup.html')

@flask_app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@flask_app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user['role'] == 'student':
        return render_template('dashboard/student_dashboard.html', user=user)
    else:
        return render_template('dashboard/teacher_dashboard.html', user=user)

@flask_app.route('/quiz')
def quiz():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('quiz/quiz_interface.html', user=session['user'])

@flask_app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('quiz/history.html', user=session['user'])

@flask_app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session['user'])

# API Routes
@flask_app.route('/api/generate_quiz', methods=['POST'])
def api_generate_quiz():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    topic = data.get('topic')
    difficulty = data.get('difficulty')
    num_questions = data.get('num_questions', 5)
    
    try:
        logger.info(f"Generating quiz: topic={topic}, difficulty={difficulty}, questions={num_questions}")
        
        # Generate questions using IBM Granite model
        questions_data = watsonx_service.generate_quiz_questions(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions
        )
        
        quiz_id = f"quiz_{datetime.now().timestamp()}"
        quiz = {
            'id': quiz_id,
            'title': f"{topic} Quiz - {difficulty.title()}",
            'topic': topic,
            'difficulty': difficulty,
            'questions': questions_data,
            'time_limit': 30,
            'created_at': datetime.now().isoformat(),
            'created_by': session['user']['id']
        }
        
        quizzes_db[quiz_id] = quiz
        logger.info(f"Quiz generated successfully: {quiz_id}")
        return jsonify(quiz)
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return jsonify({'error': f'Failed to generate quiz: {str(e)}'}), 500

@flask_app.route('/api/submit_quiz', methods=['POST'])
def api_submit_quiz():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    quiz_id = data.get('quiz_id')
    answers = data.get('answers')
    time_spent = data.get('time_spent', 0)
    
    try:
        quiz = quizzes_db.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Calculate score
        correct_answers = 0
        total_questions = len(quiz['questions'])
        
        for i, answer in enumerate(answers):
            if i < total_questions and answer == quiz['questions'][i]['correct_answer']:
                correct_answers += 1
        
        score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Generate feedback
        feedback = generate_feedback(score, quiz['topic'], correct_answers, total_questions)
        
        # Create attempt record
        attempt_id = f"attempt_{datetime.now().timestamp()}"
        attempt = {
            'id': attempt_id,
            'quiz_id': quiz_id,
            'user_id': session['user']['id'],
            'answers': answers,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'time_spent': time_spent,
            'completed_at': datetime.now().isoformat(),
            'feedback': feedback
        }
        
        attempts_db[attempt_id] = attempt
        
        # Store in Pinecone for adaptive learning
        quiz_data = {
            'user_id': session['user']['id'],
            'topic': quiz['topic'],
            'difficulty': quiz['difficulty'],
            'score': score,
            'timestamp': datetime.now().isoformat()
        }
        pinecone_service.store_quiz_attempt(session['user']['id'], quiz_data)
        
        logger.info(f"Quiz submitted: {attempt_id}, Score: {score}%")
        return jsonify(attempt)
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        return jsonify({'error': f'Failed to submit quiz: {str(e)}'}), 500

@flask_app.route('/api/quiz_history/<user_id>')
def api_quiz_history(user_id):
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_attempts = [attempt for attempt in attempts_db.values() if attempt['user_id'] == user_id]
    return jsonify(user_attempts)

@flask_app.route('/api/student_progress')
def api_student_progress():
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Get all students and their progress
    students_progress = []
    
    for email, user in users_db.items():
        if user['role'] == 'student':
            user_attempts = [attempt for attempt in attempts_db.values() if attempt['user_id'] == user['id']]
            
            if user_attempts:
                avg_score = sum(attempt['score'] for attempt in user_attempts) / len(user_attempts)
                last_activity = max(attempt['completed_at'] for attempt in user_attempts)
            else:
                avg_score = 0
                last_activity = 'Never'
            
            students_progress.append({
                'user_id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'total_quizzes': len(user_attempts),
                'average_score': round(avg_score, 1),
                'last_activity': last_activity,
                'created_at': user['created_at']
            })
    
    return jsonify(students_progress)

@flask_app.route('/api/recommendations/<user_id>')
def api_recommendations(user_id):
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    recommendations = pinecone_service.get_adaptive_recommendations(user_id)
    return jsonify(recommendations)

def generate_feedback(score: int, topic: str, correct: int, total: int) -> str:
    """Generate personalized feedback based on performance"""
    if score >= 90:
        return f"Outstanding performance! You got {correct}/{total} questions correct in {topic}. You've mastered this topic - consider exploring advanced concepts or helping other students."
    elif score >= 80:
        return f"Excellent work! You scored {correct}/{total} in {topic}. You have a strong understanding of this subject. Keep up the great work!"
    elif score >= 70:
        return f"Good job! You got {correct}/{total} questions right in {topic}. You're on the right track. Review the questions you missed to improve further."
    elif score >= 60:
        return f"You're making progress in {topic} with {correct}/{total} correct answers. Focus on the fundamentals and practice more questions to build confidence."
    else:
        return f"Keep practicing {topic}! You got {correct}/{total} questions correct. Don't get discouraged - review the basic concepts and try again. Every expert was once a beginner!"

# Gradio Interface Functions
def gradio_generate_quiz(topic, difficulty, num_questions):
    """Generate quiz using Gradio interface"""
    try:
        questions_data = watsonx_service.generate_quiz_questions(
            topic=topic,
            difficulty=difficulty,
            num_questions=int(num_questions)
        )
        
        # Format questions for display
        quiz_text = f"# 🧠 {topic} Quiz - {difficulty.title()}\n\n"
        quiz_text += f"**Generated by IBM Granite AI Model**\n\n"
        
        for i, q in enumerate(questions_data):
            quiz_text += f"## Question {i+1}\n"
            quiz_text += f"**{q['question']}**\n\n"
            
            for j, option in enumerate(q['options']):
                quiz_text += f"{chr(65+j)}. {option}\n"
            
            quiz_text += f"\n✅ **Correct Answer:** {chr(65+q['correct_answer'])}\n"
            
            if q.get('explanation'):
                quiz_text += f"💡 **Explanation:** {q['explanation']}\n"
            
            quiz_text += "\n---\n\n"
        
        return quiz_text
        
    except Exception as e:
        return f"❌ Error generating quiz: {str(e)}\n\nPlease check your IBM Watsonx configuration and try again."

def gradio_get_recommendations(user_id):
    """Get learning recommendations using Gradio"""
    try:
        recommendations = pinecone_service.get_adaptive_recommendations(user_id)
        
        rec_text = "# 🎯 Personalized Learning Recommendations\n\n"
        rec_text += "*Powered by Pinecone Vector Database & AI Analytics*\n\n"
        
        if recommendations.get('recommended_topics'):
            rec_text += "## 📚 Recommended Topics:\n"
            for topic in recommendations['recommended_topics']:
                rec_text += f"• **{topic}**\n"
            rec_text += "\n"
        
        if recommendations.get('recommended_difficulty'):
            rec_text += f"## 🎚️ Recommended Difficulty Level\n"
            rec_text += f"**{recommendations['recommended_difficulty'].title()}** - Based on your performance history\n\n"
        
        if recommendations.get('focus_areas'):
            rec_text += "## 🔍 Focus Areas for Improvement:\n"
            for area in recommendations['focus_areas']:
                rec_text += f"• **{area}** - Needs more practice\n"
            rec_text += "\n"
        
        if recommendations.get('next_steps'):
            rec_text += f"## 🚀 Next Steps:\n{recommendations['next_steps']}\n\n"
        
        if recommendations.get('learning_path'):
            rec_text += "## 🛤️ Your Personalized Learning Path:\n"
            for i, step in enumerate(recommendations['learning_path']):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                rec_text += f"{i+1}. **{step['topic']}** {priority_emoji.get(step['priority'], '🔵')}\n"
                rec_text += f"   - *Reason:* {step['reason']}\n"
                rec_text += f"   - *Suggested difficulty:* {step['suggested_difficulty']}\n\n"
        
        return rec_text
        
    except Exception as e:
        return f"❌ Error getting recommendations: {str(e)}"

def gradio_analyze_performance(user_email):
    """Analyze performance from user email"""
    try:
        user = users_db.get(user_email)
        if not user:
            return "❌ User not found. Please check the email address."
        
        user_attempts = [attempt for attempt in attempts_db.values() if attempt['user_id'] == user['id']]
        
        if not user_attempts:
            return f"📊 No quiz data found for {user['name']}. Take some quizzes first!"
        
        # Calculate statistics
        total_quizzes = len(user_attempts)
        scores = [attempt['score'] for attempt in user_attempts]
        avg_score = sum(scores) / total_quizzes
        best_score = max(scores)
        recent_scores = scores[-3:] if len(scores) >= 3 else scores
        
        analysis_text = f"# 📊 Performance Analysis for {user['name']}\n\n"
        analysis_text += "## 📈 Overall Statistics:\n"
        analysis_text += f"• **Total Quizzes Completed:** {total_quizzes}\n"
        analysis_text += f"• **Average Score:** {avg_score:.1f}%\n"
        analysis_text += f"• **Best Score:** {best_score}%\n"
        analysis_text += f"• **Recent Performance:** {sum(recent_scores)/len(recent_scores):.1f}% (last {len(recent_scores)} quizzes)\n\n"
        
        # Performance trend
        if len(scores) >= 2:
            if recent_scores[-1] > scores[0]:
                trend = "📈 Improving"
            elif recent_scores[-1] < scores[0]:
                trend = "📉 Declining"
            else:
                trend = "➡️ Stable"
            analysis_text += f"• **Performance Trend:** {trend}\n\n"
        
        # Topic analysis
        topic_performance = {}
        for attempt in user_attempts:
            quiz = quizzes_db.get(attempt['quiz_id'])
            if quiz:
                topic = quiz['topic']
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(attempt['score'])
        
        if topic_performance:
            analysis_text += "## 📚 Subject Performance:\n"
            for topic, scores in topic_performance.items():
                avg = sum(scores) / len(scores)
                status = "Strong" if avg >= 80 else "Good" if avg >= 70 else "Needs Improvement"
                analysis_text += f"• **{topic}:** {avg:.1f}% ({status})\n"
            analysis_text += "\n"
        
        # Recommendations
        analysis_text += "## 💡 Recommendations:\n"
        if avg_score >= 85:
            analysis_text += "• Excellent performance! Consider exploring advanced topics\n"
            analysis_text += "• Try harder difficulty levels to challenge yourself\n"
        elif avg_score >= 70:
            analysis_text += "• Good progress! Focus on consistency\n"
            analysis_text += "• Review topics where you scored below 80%\n"
        else:
            analysis_text += "• Focus on fundamental concepts\n"
            analysis_text += "• Take more practice quizzes in weaker subjects\n"
            analysis_text += "• Consider easier difficulty levels to build confidence\n"
        
        return analysis_text
        
    except Exception as e:
        return f"❌ Error analyzing performance: {str(e)}"

# Create Gradio Interface
def create_gradio_interface():
    """Create enhanced Gradio interface for AI features"""
    
    with gr.Blocks(title="EduTutor AI - Advanced Features", theme=gr.themes.Soft()) as gradio_interface:
        gr.Markdown("# 🧠 EduTutor AI - Advanced AI Features")
        gr.Markdown("*Powered by IBM Granite AI, Pinecone Vector Database, and Google Classroom Integration*")
        
        with gr.Tabs():
            # Quiz Generation Tab
            with gr.TabItem("🎯 AI Quiz Generator"):
                gr.Markdown("## Generate Personalized Quizzes with IBM Granite AI")
                
                with gr.Row():
                    topic_input = gr.Dropdown(
                        choices=["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", 
                                "History", "Geography", "Literature", "Economics", "Psychology"],
                        label="Select Topic",
                        value="Mathematics"
                    )
                    difficulty_input = gr.Dropdown(
                        choices=["easy", "medium", "hard"],
                        label="Difficulty Level",
                        value="medium"
                    )
                    num_questions_input = gr.Slider(
                        minimum=3,
                        maximum=15,
                        value=5,
                        step=1,
                        label="Number of Questions"
                    )
                
                generate_btn = gr.Button("🚀 Generate Quiz with IBM Granite AI", variant="primary", size="lg")
                quiz_output = gr.Markdown(label="Generated Quiz")
                
                generate_btn.click(
                    gradio_generate_quiz,
                    inputs=[topic_input, difficulty_input, num_questions_input],
                    outputs=quiz_output
                )
            
            # Recommendations Tab
            with gr.TabItem("💡 Learning Recommendations"):
                gr.Markdown("## Get Personalized Learning Recommendations")
                gr.Markdown("*Powered by Pinecone Vector Database and AI Analytics*")
                
                user_id_input = gr.Textbox(
                    label="User ID",
                    placeholder="Enter user ID (e.g., student1, teacher1)",
                    value="student1"
                )
                
                rec_btn = gr.Button("🎯 Get AI Recommendations", variant="primary", size="lg")
                rec_output = gr.Markdown(label="Personalized Recommendations")
                
                rec_btn.click(
                    gradio_get_recommendations,
                    inputs=user_id_input,
                    outputs=rec_output
                )
            
            # Performance Analysis Tab
            with gr.TabItem("📊 Performance Analysis"):
                gr.Markdown("## Analyze Learning Performance")
                gr.Markdown("*Advanced analytics powered by AI*")
                
                user_email_input = gr.Textbox(
                    label="User Email",
                    placeholder="Enter user email (e.g., student@demo.com)",
                    value="student@demo.com"
                )
                
                analyze_btn = gr.Button("📈 Analyze Performance", variant="primary", size="lg")
                analysis_output = gr.Markdown(label="Performance Analysis")
                
                analyze_btn.click(
                    gradio_analyze_performance,
                    inputs=user_email_input,
                    outputs=analysis_output
                )
            
            # AI Chat Assistant Tab
            with gr.TabItem("🤖 AI Learning Assistant"):
                gr.Markdown("## Chat with Your AI Learning Assistant")
                gr.Markdown("*Powered by IBM Granite AI Model*")
                
                chatbot = gr.Chatbot(label="EduTutor AI Assistant", height=400)
                msg = gr.Textbox(label="Ask a question about learning...", placeholder="Type your question here...")
                clear = gr.Button("Clear Chat")
                
                def respond(message, chat_history):
                    # Enhanced AI responses
                    responses = {
                        "hello": "Hello! I'm your AI learning assistant powered by IBM Granite AI. How can I help you with your studies today?",
                        "quiz": "I can help you generate personalized quizzes using IBM's advanced AI! What topic would you like to practice?",
                        "study": "Great question! Based on your performance data from Pinecone, I recommend focusing on your weak areas first. Would you like specific recommendations?",
                        "help": "I can assist with:\n• Quiz generation using IBM Granite AI\n• Personalized learning recommendations\n• Performance analysis\n• Study tips and strategies\n• Topic explanations",
                        "granite": "IBM Granite is a powerful foundation model that generates high-quality educational content. It's specifically designed for instruction and can create personalized quizzes tailored to your learning level!",
                        "pinecone": "Pinecone is our vector database that stores your learning patterns and helps create personalized recommendations. It analyzes your quiz history to suggest the best topics and difficulty levels for you!",
                        "score": "Your quiz scores are analyzed using AI to identify patterns and areas for improvement. The system tracks your progress over time and adapts to your learning style.",
                        "difficulty": "The AI automatically adjusts quiz difficulty based on your performance. If you're scoring well, it will suggest harder questions. If you're struggling, it will recommend easier content to build confidence."
                    }
                    
                    # Simple keyword matching with enhanced responses
                    response = "I'm here to help with your learning journey! I use IBM Granite AI to generate personalized quizzes and Pinecone vector database to track your progress. You can ask me about:\n\n• Generating quizzes\n• Study recommendations\n• Performance analysis\n• Learning strategies\n• Any educational topic!"
                    
                    message_lower = message.lower()
                    for key, value in responses.items():
                        if key in message_lower:
                            response = value
                            break
                    
                    chat_history.append((message, response))
                    return "", chat_history
                
                msg.submit(respond, [msg, chatbot], [msg, chatbot])
                clear.click(lambda: None, None, chatbot, queue=False)
        
        gr.Markdown("---")
        gr.Markdown("### 🔗 Quick Access Links")
        gr.Markdown("• [Flask Web Application](http://localhost:5000) - Complete learning platform")
        gr.Markdown("• [Student Dashboard](http://localhost:5000/dashboard) - Student interface")
        gr.Markdown("• [Teacher Dashboard](http://localhost:5000/dashboard) - Teacher interface")
        gr.Markdown("• [Take Quiz](http://localhost:5000/quiz) - Interactive quiz interface")
    
    return gradio_interface

# Start Flask app in a separate thread
def start_flask_app():
    """Start Flask app"""
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    # Create templates directory and files
    os.makedirs('templates', exist_ok=True)
    os.makedirs('templates/auth', exist_ok=True)
    os.makedirs('templates/dashboard', exist_ok=True)
    os.makedirs('templates/quiz', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Start Flask app in background
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Wait a moment for Flask to start
    time.sleep(2)
    
    # Create and launch Gradio interface
    gradio_interface = create_gradio_interface()
    
    print("🚀 EduTutor AI is starting...")
    print("📊 Flask Web App: http://localhost:5000")
    print("🤖 Gradio AI Interface: http://localhost:7860")
    print("\n🔑 Demo Accounts:")
    print("   Student: student@demo.com / password")
    print("   Teacher: teacher@demo.com / password")
    
    # Launch Gradio interface
    gradio_interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )