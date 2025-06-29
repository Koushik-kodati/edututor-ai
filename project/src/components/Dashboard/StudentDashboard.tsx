import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  Trophy, 
  Clock, 
  TrendingUp, 
  BookOpen, 
  Target,
  Calendar,
  Award
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { QuizAttempt } from '../../types';

const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [recentQuizzes, setRecentQuizzes] = useState<QuizAttempt[]>([]);
  const [stats, setStats] = useState({
    totalQuizzes: 12,
    averageScore: 85,
    timeSpent: 240,
    streak: 5,
  });

  const quickActions = [
    {
      title: 'Take New Quiz',
      description: 'Start a personalized quiz',
      icon: Brain,
      color: 'bg-primary-500',
      href: '/quiz',
    },
    {
      title: 'View Progress',
      description: 'Check your learning analytics',
      icon: TrendingUp,
      color: 'bg-success-500',
      href: '/history',
    },
    {
      title: 'Browse Courses',
      description: 'Explore available courses',
      icon: BookOpen,
      color: 'bg-warning-500',
      href: '/courses',
    },
    {
      title: 'Achievements',
      description: 'View your badges and rewards',
      icon: Trophy,
      color: 'bg-purple-500',
      href: '/achievements',
    },
  ];

  const recentActivity = [
    { topic: 'Mathematics', score: 92, date: '2024-01-15', difficulty: 'Medium' },
    { topic: 'Physics', score: 78, date: '2024-01-14', difficulty: 'Hard' },
    { topic: 'Chemistry', score: 88, date: '2024-01-13', difficulty: 'Easy' },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-8 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.name}!</h1>
            <p className="text-primary-100 text-lg">Ready to continue your learning journey?</p>
          </div>
          <div className="hidden md:block">
            <div className="bg-white/10 rounded-full p-4">
              <Brain className="w-12 h-12 text-white" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Total Quizzes', value: stats.totalQuizzes, icon: Target, color: 'text-primary-600' },
          { label: 'Average Score', value: `${stats.averageScore}%`, icon: Trophy, color: 'text-success-600' },
          { label: 'Time Spent', value: `${stats.timeSpent}m`, icon: Clock, color: 'text-warning-600' },
          { label: 'Current Streak', value: `${stats.streak} days`, icon: Award, color: 'text-purple-600' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => (
            <motion.a
              key={action.title}
              href={action.href}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow group"
            >
              <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{action.title}</h3>
              <p className="text-sm text-gray-600">{action.description}</p>
            </motion.a>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Quiz Results</h3>
          <div className="space-y-4">
            {recentActivity.map((quiz, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{quiz.topic}</p>
                  <p className="text-sm text-gray-600">{quiz.date} • {quiz.difficulty}</p>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${quiz.score >= 80 ? 'text-success-600' : quiz.score >= 60 ? 'text-warning-600' : 'text-error-600'}`}>
                    {quiz.score}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Goals</h3>
          <div className="space-y-4">
            <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
              <div className="flex items-center justify-between mb-2">
                <p className="font-medium text-primary-900">Mathematics Mastery</p>
                <span className="text-sm text-primary-600">75%</span>
              </div>
              <div className="w-full bg-primary-200 rounded-full h-2">
                <div className="bg-primary-600 h-2 rounded-full" style={{ width: '75%' }}></div>
              </div>
            </div>
            
            <div className="p-4 bg-success-50 rounded-lg border border-success-200">
              <div className="flex items-center justify-between mb-2">
                <p className="font-medium text-success-900">Physics Fundamentals</p>
                <span className="text-sm text-success-600">60%</span>
              </div>
              <div className="w-full bg-success-200 rounded-full h-2">
                <div className="bg-success-600 h-2 rounded-full" style={{ width: '60%' }}></div>
              </div>
            </div>
            
            <div className="p-4 bg-warning-50 rounded-lg border border-warning-200">
              <div className="flex items-center justify-between mb-2">
                <p className="font-medium text-warning-900">Chemistry Basics</p>
                <span className="text-sm text-warning-600">45%</span>
              </div>
              <div className="w-full bg-warning-200 rounded-full h-2">
                <div className="bg-warning-600 h-2 rounded-full" style={{ width: '45%' }}></div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default StudentDashboard;