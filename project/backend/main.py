import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Import services
from services.watsonx_service import watsonx_service
from services.pinecone_service import pinecone_service
from services.google_classroom_service import google_classroom_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EduTutor AI Backend", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class UserLogin(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class QuizGenerationRequest(BaseModel):
    topic: str
    difficulty: str
    num_questions: int = 5
    user_id: Optional[str] = None

class QuizSubmissionRequest(BaseModel):
    quiz_id: str
    answers: List[int]
    time_spent: int = 0

class DiagnosticTestRequest(BaseModel):
    user_id: str
    subjects: List[str]

class Question(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None

class Quiz(BaseModel):
    id: str
    title: str
    topic: str
    difficulty: str
    questions: List[Question]
    time_limit: Optional[int] = 30
    created_at: str
    is_diagnostic: bool = False

class QuizAttempt(BaseModel):
    id: str
    quiz_id: str
    user_id: str
    answers: List[int]
    score: int
    completed_at: str
    time_spent: int
    feedback: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    learning_preferences: Dict[str, Any] = {}
    diagnostic_completed: bool = False

# Mock data storage (replace with actual database)
users_db = {
    "student@demo.com": {
        "id": "student1",
        "email": "student@demo.com",
        "name": "Demo Student",
        "password": "password",
        "role": "student",
        "learning_preferences": {},
        "diagnostic_completed": False
    },
    "teacher@demo.com": {
        "id": "teacher1",
        "email": "teacher@demo.com",
        "name": "Demo Teacher",
        "password": "password",
        "role": "educator",
        "learning_preferences": {},
        "diagnostic_completed": True
    }
}

quizzes_db = {}
attempts_db = {}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    # In production, validate JWT token
    for user in users_db.values():
        if user["id"] == token:
            return user
    raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
async def root():
    return {"message": "EduTutor AI Backend v2.0 is running!", "features": ["IBM Watsonx", "Pinecone", "Google Classroom"]}

@app.post("/auth/login")
async def login(request: UserLogin):
    """User login with email and password"""
    try:
        user = users_db.get(request.email)
        if not user or user["password"] != request.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Return user data with token (user ID as token for demo)
        return {
            "token": user["id"],
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "diagnostic_completed": user["diagnostic_completed"]
            }
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/google")
async def google_auth(request: GoogleAuthRequest):
    """Google OAuth authentication"""
    try:
        # Exchange code for credentials
        credentials = google_classroom_service.exchange_code_for_credentials(
            request.code, request.redirect_uri
        )
        
        # Mock user creation from Google
        user_data = {
            "id": "google_user_1",
            "email": "user@gmail.com",
            "name": "Google User",
            "role": "student",
            "diagnostic_completed": False
        }
        
        return {
            "token": user_data["id"],
            "user": user_data
        }
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=500, detail="Google authentication failed")

@app.post("/quiz/diagnostic", response_model=Quiz)
async def create_diagnostic_test(request: DiagnosticTestRequest):
    """Create diagnostic test for new users"""
    try:
        logger.info(f"Creating diagnostic test for user: {request.user_id}")
        
        # Generate diagnostic questions across multiple subjects
        all_questions = []
        question_id = 1
        
        for subject in request.subjects:
            questions = watsonx_service.generate_quiz_questions(
                topic=subject,
                difficulty="medium",
                num_questions=3
            )
            
            for q in questions:
                q["id"] = f"diag_{question_id}"
                question_id += 1
                all_questions.append(Question(**q))
        
        quiz_id = f"diagnostic_{datetime.now().timestamp()}"
        quiz = Quiz(
            id=quiz_id,
            title="Diagnostic Assessment",
            topic="Multi-Subject",
            difficulty="adaptive",
            questions=all_questions,
            time_limit=45,
            created_at=datetime.now().isoformat(),
            is_diagnostic=True
        )
        
        quizzes_db[quiz_id] = quiz
        logger.info(f"Created diagnostic test with {len(all_questions)} questions")
        return quiz
        
    except Exception as e:
        logger.error(f"Error creating diagnostic test: {e}")
        raise HTTPException(status_code=500, detail="Failed to create diagnostic test")

@app.post("/quiz/generate", response_model=Quiz)
async def generate_quiz(request: QuizGenerationRequest, current_user: dict = Depends(get_current_user)):
    """Generate personalized quiz using IBM Granite model"""
    try:
        logger.info(f"Generating quiz for user: {current_user['id']}, topic: {request.topic}")
        
        # Get user's learning preferences for personalization
        user_preferences = pinecone_service.get_adaptive_recommendations(current_user["id"])
        
        # Adjust difficulty based on user performance
        adjusted_difficulty = request.difficulty
        if user_preferences.get("recommended_difficulty"):
            adjusted_difficulty = user_preferences["recommended_difficulty"]
        
        # Generate questions using Watsonx
        questions_data = watsonx_service.generate_quiz_questions(
            topic=request.topic,
            difficulty=adjusted_difficulty,
            num_questions=request.num_questions
        )
        
        # Create Question objects
        questions = []
        for i, q_data in enumerate(questions_data):
            question = Question(
                id=f"q_{i+1}",
                question=q_data["question"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation")
            )
            questions.append(question)
        
        quiz_id = f"quiz_{datetime.now().timestamp()}"
        quiz = Quiz(
            id=quiz_id,
            title=f"{request.topic} Quiz - {adjusted_difficulty.title()}",
            topic=request.topic,
            difficulty=adjusted_difficulty,
            questions=questions,
            time_limit=30,
            created_at=datetime.now().isoformat()
        )
        
        # Store quiz
        quizzes_db[quiz_id] = quiz
        
        logger.info(f"Generated quiz with ID: {quiz_id}")
        return quiz
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@app.post("/quiz/submit", response_model=QuizAttempt)
async def submit_quiz(request: QuizSubmissionRequest, current_user: dict = Depends(get_current_user)):
    """Submit quiz answers and get results with AI feedback"""
    try:
        logger.info(f"Submitting quiz: {request.quiz_id} for user: {current_user['id']}")
        
        # Get quiz from storage
        quiz = quizzes_db.get(request.quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Calculate score and analyze performance
        correct_answers = 0
        incorrect_topics = []
        
        for i, answer in enumerate(request.answers):
            if i < len(quiz.questions):
                if answer == quiz.questions[i].correct_answer:
                    correct_answers += 1
                else:
                    incorrect_topics.append(quiz.topic)
        
        score = int((correct_answers / len(quiz.questions)) * 100)
        
        # Generate AI feedback
        feedback = self._generate_feedback(score, quiz.topic, incorrect_topics)
        
        # Create attempt record
        attempt_id = f"attempt_{datetime.now().timestamp()}"
        attempt = QuizAttempt(
            id=attempt_id,
            quiz_id=request.quiz_id,
            user_id=current_user["id"],
            answers=request.answers,
            score=score,
            completed_at=datetime.now().isoformat(),
            time_spent=request.time_spent,
            feedback=feedback
        )
        
        # Store attempt
        attempts_db[attempt_id] = attempt
        
        # Store in Pinecone for adaptive learning
        quiz_data = {
            "user_id": current_user["id"],
            "topic": quiz.topic,
            "difficulty": quiz.difficulty,
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "is_diagnostic": quiz.is_diagnostic
        }
        pinecone_service.store_quiz_attempt(current_user["id"], quiz_data)
        
        # Update user diagnostic status if this was a diagnostic test
        if quiz.is_diagnostic:
            users_db[current_user["email"]]["diagnostic_completed"] = True
        
        logger.info(f"Quiz submitted with score: {score}%")
        return attempt
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit quiz: {str(e)}")

def _generate_feedback(score: int, topic: str, incorrect_topics: List[str]) -> str:
    """Generate personalized feedback using AI"""
    if score >= 90:
        return f"Excellent work on {topic}! You've mastered this topic. Consider exploring advanced concepts."
    elif score >= 70:
        return f"Good job on {topic}! You have a solid understanding. Review the areas you missed for improvement."
    elif score >= 50:
        return f"You're making progress in {topic}. Focus on the fundamentals and practice more questions."
    else:
        return f"Keep practicing {topic}! Consider reviewing the basic concepts and taking additional quizzes."

@app.get("/quiz/history/{user_id}")
async def get_quiz_history(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get quiz history for a user"""
    try:
        # Get from Pinecone
        history = pinecone_service.get_user_quiz_history(user_id)
        
        # Also get from local storage
        user_attempts = [attempt for attempt in attempts_db.values() if attempt.user_id == user_id]
        
        return {
            "attempts": user_attempts,
            "analytics": history,
            "total_quizzes": len(user_attempts),
            "average_score": sum(a.score for a in user_attempts) / len(user_attempts) if user_attempts else 0
        }
    except Exception as e:
        logger.error(f"Error getting quiz history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quiz history")

@app.get("/students/progress")
async def get_student_progress(current_user: dict = Depends(get_current_user)):
    """Get progress data for all students (educator view)"""
    try:
        if current_user["role"] != "educator":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all student attempts
        student_progress = {}
        for attempt in attempts_db.values():
            user_id = attempt.user_id
            if user_id not in student_progress:
                # Find user info
                user_info = None
                for user in users_db.values():
                    if user["id"] == user_id:
                        user_info = user
                        break
                
                if user_info:
                    student_progress[user_id] = {
                        "userId": user_id,
                        "userName": user_info["name"],
                        "email": user_info["email"],
                        "totalQuizzes": 0,
                        "scores": [],
                        "lastActivity": None,
                        "topicProgress": {}
                    }
            
            if user_id in student_progress:
                student_progress[user_id]["totalQuizzes"] += 1
                student_progress[user_id]["scores"].append(attempt.score)
                student_progress[user_id]["lastActivity"] = attempt.completed_at
                
                # Get quiz info for topic
                quiz = quizzes_db.get(attempt.quiz_id)
                if quiz:
                    topic = quiz.topic
                    if topic not in student_progress[user_id]["topicProgress"]:
                        student_progress[user_id]["topicProgress"][topic] = []
                    student_progress[user_id]["topicProgress"][topic].append(attempt.score)
        
        # Calculate averages
        for user_id, progress in student_progress.items():
            if progress["scores"]:
                progress["averageScore"] = sum(progress["scores"]) / len(progress["scores"])
            else:
                progress["averageScore"] = 0
            
            # Calculate topic averages
            for topic, scores in progress["topicProgress"].items():
                progress["topicProgress"][topic] = sum(scores) / len(scores)
        
        return list(student_progress.values())
        
    except Exception as e:
        logger.error(f"Error getting student progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student progress")

@app.post("/classroom/sync")
async def sync_classrooms(current_user: dict = Depends(get_current_user)):
    """Sync with Google Classroom"""
    try:
        # Sync classroom data
        classroom_data = google_classroom_service.sync_classroom_data()
        
        return {
            "success": True,
            "courses": classroom_data.get("courses", []),
            "total_courses": classroom_data.get("total_courses", 0),
            "students_by_course": classroom_data.get("students_by_course", {})
        }
    except Exception as e:
        logger.error(f"Error syncing classrooms: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync classrooms")

@app.get("/classroom/courses")
async def get_courses(current_user: dict = Depends(get_current_user)):
    """Get available courses"""
    try:
        courses = google_classroom_service.get_courses()
        return courses
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get courses")

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get adaptive learning recommendations"""
    try:
        recommendations = pinecone_service.get_adaptive_recommendations(user_id)
        similar_users = pinecone_service.get_similar_users(user_id)
        
        return {
            "recommendations": recommendations,
            "similar_learners": similar_users,
            "personalized": True
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@app.get("/analytics/dashboard")
async def get_analytics_dashboard(current_user: dict = Depends(get_current_user)):
    """Get comprehensive analytics dashboard data"""
    try:
        if current_user["role"] != "educator":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Calculate overall statistics
        total_students = len([u for u in users_db.values() if u["role"] == "student"])
        total_quizzes = len(attempts_db)
        
        # Topic performance analysis
        topic_stats = {}
        for attempt in attempts_db.values():
            quiz = quizzes_db.get(attempt.quiz_id)
            if quiz:
                topic = quiz.topic
                if topic not in topic_stats:
                    topic_stats[topic] = {"scores": [], "attempts": 0}
                topic_stats[topic]["scores"].append(attempt.score)
                topic_stats[topic]["attempts"] += 1
        
        # Calculate topic averages
        for topic, stats in topic_stats.items():
            stats["average"] = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
        
        return {
            "overview": {
                "total_students": total_students,
                "total_quizzes": total_quizzes,
                "active_today": total_students // 2,  # Mock data
                "completion_rate": 85
            },
            "topic_performance": topic_stats,
            "recent_activity": list(attempts_db.values())[-10:],  # Last 10 attempts
            "trends": {
                "weekly_growth": 15,
                "engagement_rate": 78,
                "average_score_trend": 5
            }
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)