export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'educator';
  avatar?: string;
  googleId?: string;
}

export interface Quiz {
  id: string;
  title: string;
  topic: string;
  difficulty: 'easy' | 'medium' | 'hard';
  questions: Question[];
  timeLimit?: number;
  createdAt: string;
}

export interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation?: string;
}

export interface QuizAttempt {
  id: string;
  quizId: string;
  userId: string;
  answers: number[];
  score: number;
  completedAt: string;
  timeSpent: number;
}

export interface StudentProgress {
  userId: string;
  userName: string;
  totalQuizzes: number;
  averageScore: number;
  lastActivity: string;
  topicProgress: { [topic: string]: number };
}

export interface Course {
  id: string;
  name: string;
  description: string;
  enrollmentCode?: string;
}