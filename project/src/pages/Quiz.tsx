import React, { useState } from 'react';
import { motion } from 'framer-motion';
import QuizSetup from '../components/Quiz/QuizSetup';
import QuizInterface from '../components/Quiz/QuizInterface';
import { Quiz as QuizType, QuizAttempt } from '../types';
import { apiService } from '../services/api';

const Quiz: React.FC = () => {
  const [currentQuiz, setCurrentQuiz] = useState<QuizType | null>(null);
  const [quizResult, setQuizResult] = useState<QuizAttempt | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleStartQuiz = async (topic: string, difficulty: string, numQuestions: number) => {
    setIsLoading(true);
    try {
      // Mock quiz generation for demo
      const mockQuiz: QuizType = {
        id: Date.now().toString(),
        title: `${topic} Quiz`,
        topic,
        difficulty: difficulty as 'easy' | 'medium' | 'hard',
        timeLimit: 30,
        createdAt: new Date().toISOString(),
        questions: Array.from({ length: numQuestions }, (_, i) => ({
          id: `q${i + 1}`,
          question: `Sample ${topic} question ${i + 1}?`,
          options: [
            'Option A - This is the first possible answer',
            'Option B - This is the second possible answer',
            'Option C - This is the third possible answer',
            'Option D - This is the fourth possible answer',
          ],
          correctAnswer: Math.floor(Math.random() * 4),
          explanation: `This is the explanation for question ${i + 1}.`,
        })),
      };
      
      setCurrentQuiz(mockQuiz);
    } catch (error) {
      console.error('Failed to generate quiz:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitQuiz = async (answers: number[]) => {
    if (!currentQuiz) return;

    try {
      // Calculate score
      let correctAnswers = 0;
      currentQuiz.questions.forEach((question, index) => {
        if (answers[index] === question.correctAnswer) {
          correctAnswers++;
        }
      });

      const score = Math.round((correctAnswers / currentQuiz.questions.length) * 100);
      
      const result: QuizAttempt = {
        id: Date.now().toString(),
        quizId: currentQuiz.id,
        userId: 'current-user',
        answers,
        score,
        completedAt: new Date().toISOString(),
        timeSpent: 0,
      };

      setQuizResult(result);
      setCurrentQuiz(null);
    } catch (error) {
      console.error('Failed to submit quiz:', error);
    }
  };

  const handleExitQuiz = () => {
    setCurrentQuiz(null);
  };

  const handleRetakeQuiz = () => {
    setQuizResult(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Generating your personalized quiz...</p>
        </div>
      </div>
    );
  }

  if (currentQuiz) {
    return (
      <QuizInterface
        quiz={currentQuiz}
        onSubmit={handleSubmitQuiz}
        onExit={handleExitQuiz}
      />
    );
  }

  if (quizResult) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl mx-auto"
      >
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className={`w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center ${
            quizResult.score >= 80 ? 'bg-success-100' : quizResult.score >= 60 ? 'bg-warning-100' : 'bg-error-100'
          }`}>
            <span className={`text-3xl font-bold ${
              quizResult.score >= 80 ? 'text-success-600' : quizResult.score >= 60 ? 'text-warning-600' : 'text-error-600'
            }`}>
              {quizResult.score}%
            </span>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quiz Complete!</h2>
          <p className="text-gray-600 mb-8">
            {quizResult.score >= 80 
              ? 'Excellent work! You have a strong understanding of this topic.'
              : quizResult.score >= 60
              ? 'Good job! There\'s room for improvement, but you\'re on the right track.'
              : 'Keep practicing! Review the material and try again to improve your score.'
            }
          </p>
          
          <div className="flex space-x-4">
            <button
              onClick={handleRetakeQuiz}
              className="flex-1 bg-primary-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-primary-700 transition-colors"
            >
              Take Another Quiz
            </button>
            <button
              onClick={() => window.location.href = '/history'}
              className="flex-1 border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              View History
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  return <QuizSetup onStartQuiz={handleStartQuiz} />;
};

export default Quiz;