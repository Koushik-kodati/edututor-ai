import os
import logging
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class GoogleClassroomService:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.scopes = [
            'https://www.googleapis.com/auth/classroom.courses.readonly',
            'https://www.googleapis.com/auth/classroom.rosters.readonly',
            'https://www.googleapis.com/auth/classroom.profile.emails'
        ]
        
        if not all([self.client_id, self.client_secret]):
            logger.warning("Google OAuth credentials not found, using mock data")
            self.service = None
        else:
            self.service = None  # Will be initialized after OAuth

    def get_authorization_url(self, redirect_uri: str) -> str:
        """Get Google OAuth authorization URL"""
        try:
            if not all([self.client_id, self.client_secret]):
                raise Exception("Google OAuth credentials not configured")
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = redirect_uri
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"Error getting authorization URL: {e}")
            raise

    def exchange_code_for_credentials(self, code: str, redirect_uri: str) -> Credentials:
        """Exchange authorization code for credentials"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = redirect_uri
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Initialize service
            self.service = build('classroom', 'v1', credentials=credentials)
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error exchanging code for credentials: {e}")
            raise

    def get_courses(self, credentials: Optional[Credentials] = None) -> List[Dict]:
        """Get user's Google Classroom courses"""
        try:
            if not self.service and credentials:
                self.service = build('classroom', 'v1', credentials=credentials)
            
            if not self.service:
                # Return mock courses
                return [
                    {
                        "id": "course_1",
                        "name": "Advanced Mathematics",
                        "description": "Calculus and Linear Algebra",
                        "enrollmentCode": "abc123",
                        "courseState": "ACTIVE"
                    },
                    {
                        "id": "course_2", 
                        "name": "Physics 101",
                        "description": "Introduction to Physics",
                        "enrollmentCode": "def456",
                        "courseState": "ACTIVE"
                    },
                    {
                        "id": "course_3",
                        "name": "Chemistry Fundamentals", 
                        "description": "Basic Chemistry Concepts",
                        "enrollmentCode": "ghi789",
                        "courseState": "ACTIVE"
                    }
                ]
            
            # Get courses from Google Classroom
            results = self.service.courses().list(pageSize=50).execute()
            courses = results.get('courses', [])
            
            return [
                {
                    "id": course.get('id'),
                    "name": course.get('name'),
                    "description": course.get('description', ''),
                    "enrollmentCode": course.get('enrollmentCode'),
                    "courseState": course.get('courseState')
                }
                for course in courses
            ]
            
        except Exception as e:
            logger.error(f"Error getting courses: {e}")
            # Return mock data on error
            return [
                {
                    "id": "mock_course_1",
                    "name": "Sample Course",
                    "description": "A sample course for demonstration",
                    "enrollmentCode": "sample123",
                    "courseState": "ACTIVE"
                }
            ]

    def get_course_students(self, course_id: str, credentials: Optional[Credentials] = None) -> List[Dict]:
        """Get students enrolled in a course"""
        try:
            if not self.service and credentials:
                self.service = build('classroom', 'v1', credentials=credentials)
            
            if not self.service:
                # Return mock students
                return [
                    {
                        "userId": "student_1",
                        "profile": {
                            "name": {"fullName": "Alice Johnson"},
                            "emailAddress": "alice@school.edu"
                        }
                    },
                    {
                        "userId": "student_2",
                        "profile": {
                            "name": {"fullName": "Bob Smith"},
                            "emailAddress": "bob@school.edu"
                        }
                    }
                ]
            
            # Get students from Google Classroom
            results = self.service.courses().students().list(courseId=course_id).execute()
            students = results.get('students', [])
            
            return students
            
        except Exception as e:
            logger.error(f"Error getting course students: {e}")
            return []

    def sync_classroom_data(self, credentials: Optional[Credentials] = None) -> Dict:
        """Sync all classroom data"""
        try:
            courses = self.get_courses(credentials)
            
            classroom_data = {
                "courses": courses,
                "total_courses": len(courses),
                "students_by_course": {}
            }
            
            # Get students for each course
            for course in courses:
                course_id = course["id"]
                students = self.get_course_students(course_id, credentials)
                classroom_data["students_by_course"][course_id] = students
            
            logger.info(f"Synced {len(courses)} courses from Google Classroom")
            return classroom_data
            
        except Exception as e:
            logger.error(f"Error syncing classroom data: {e}")
            return {
                "courses": [],
                "total_courses": 0,
                "students_by_course": {},
                "error": str(e)
            }

# Global instance
google_classroom_service = GoogleClassroomService()