import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  TrendingUp, 
  BookOpen, 
  Award,
  Clock,
  Target,
  BarChart3,
  Calendar
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { StudentProgress } from '../../types';

const EducatorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [students, setStudents] = useState<StudentProgress[]>([]);
  const [stats, setStats] = useState({
    totalStudents: 45,
    activeToday: 32,
    averageScore: 78,
    completionRate: 85,
  });

  const recentActivity = [
    { student: 'Alice Johnson', quiz: 'Algebra Basics', score: 92, time: '2 hours ago' },
    { student: 'Bob Smith', quiz: 'Physics Laws', score: 78, time: '3 hours ago' },
    { student: 'Carol Davis', quiz: 'Chemistry Elements', score: 88, time: '5 hours ago' },
    { student: 'David Wilson', quiz: 'Geometry', score: 95, time: '6 hours ago' },
  ];

  const topPerformers = [
    { name: 'Alice Johnson', score: 94, quizzes: 15 },
    { name: 'David Wilson', score: 92, quizzes: 12 },
    { name: 'Emma Brown', score: 89, quizzes: 18 },
    { name: 'Frank Miller', score: 87, quizzes: 14 },
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
            <h1 className="text-3xl font-bold mb-2">Good morning, {user?.name}!</h1>
            <p className="text-primary-100 text-lg">Here's how your students are performing today</p>
          </div>
          <div className="hidden md:block">
            <div className="bg-white/10 rounded-full p-4">
              <Users className="w-12 h-12 text-white" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Total Students', value: stats.totalStudents, icon: Users, color: 'text-primary-600' },
          { label: 'Active Today', value: stats.activeToday, icon: Clock, color: 'text-success-600' },
          { label: 'Average Score', value: `${stats.averageScore}%`, icon: Target, color: 'text-warning-600' },
          { label: 'Completion Rate', value: `${stats.completionRate}%`, icon: Award, color: 'text-purple-600' },
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

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Recent Student Activity</h3>
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All
            </button>
          </div>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-medium text-sm">
                      {activity.student.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{activity.student}</p>
                    <p className="text-sm text-gray-600">{activity.quiz}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${activity.score >= 80 ? 'text-success-600' : activity.score >= 60 ? 'text-warning-600' : 'text-error-600'}`}>
                    {activity.score}%
                  </p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Top Performers */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Top Performers</h3>
          <div className="space-y-4">
            {topPerformers.map((student, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                    index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-500' : 'bg-primary-500'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{student.name}</p>
                    <p className="text-xs text-gray-600">{student.quizzes} quizzes</p>
                  </div>
                </div>
                <span className="text-success-600 font-bold">{student.score}%</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: 'View All Students',
              description: 'Manage student progress and performance',
              icon: Users,
              color: 'bg-primary-500',
              href: '/students',
            },
            {
              title: 'Analytics Dashboard',
              description: 'Detailed insights and reports',
              icon: BarChart3,
              color: 'bg-success-500',
              href: '/analytics',
            },
            {
              title: 'Course Management',
              description: 'Manage courses and assignments',
              icon: BookOpen,
              color: 'bg-warning-500',
              href: '/courses',
            },
          ].map((action, index) => (
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
    </div>
  );
};

export default EducatorDashboard;