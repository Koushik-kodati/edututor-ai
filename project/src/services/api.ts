import axios from 'axios';
import { Quiz, QuizAttempt, StudentProgress, Course } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const user = localStorage.getItem('user');
  if (user) {
    const { id } = JSON.parse(user);
    config.headers.Authorization = `Bearer ${id}`;
  }
  return config;
});

export const apiService = {
  // Quiz operations
  generateQuiz: async (topic: string, difficulty: string, numQuestions: number = 5): Promise<Quiz> => {
    const response = await api.post('/quiz/generate', {
      topic,
      difficulty,
      num_questions: numQuestions,
    });
    return response.data;
  },

  submitQuiz: async (quizId: string, answers: number[]): Promise<QuizAttempt> => {
    const response = await api.post('/quiz/submit', {
      quiz_id: quizId,
      answers,
    });
    return response.data;
  },

  getQuizHistory: async (userId: string): Promise<QuizAttempt[]> => {
    const response = await api.get(`/quiz/history/${userId}`);
    return response.data;
  },

  // Student progress
  getStudentProgress: async (): Promise<StudentProgress[]> => {
    const response = await api.get('/students/progress');
    return response.data;
  },

  // Google Classroom integration
  syncClassrooms: async (): Promise<Course[]> => {
    const response = await api.post('/classroom/sync');
    return response.data;
  },

  getCourses: async (): Promise<Course[]> => {
    const response = await api.get('/classroom/courses');
    return response.data;
  },
};

export default api;