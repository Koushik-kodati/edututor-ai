import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Clock, Target, BookOpen, Zap } from 'lucide-react';

interface QuizSetupProps {
  onStartQuiz: (topic: string, difficulty: string, numQuestions: number) => void;
}

const QuizSetup: React.FC<QuizSetupProps> = ({ onStartQuiz }) => {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [isLoading, setIsLoading] = useState(false);

  const topics = [
    'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science',
    'History', 'Geography', 'Literature', 'Economics', 'Psychology'
  ];

  const difficulties = [
    { value: 'easy', label: 'Easy', description: 'Basic concepts and fundamentals', color: 'text-success-600' },
    { value: 'medium', label: 'Medium', description: 'Intermediate level questions', color: 'text-warning-600' },
    { value: 'hard', label: 'Hard', description: 'Advanced and challenging', color: 'text-error-600' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic) return;
    
    setIsLoading(true);
    try {
      await onStartQuiz(topic, difficulty, numQuestions);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-xl p-8"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mx-auto mb-4">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Create Your Quiz</h1>
          <p className="text-gray-600">Customize your learning experience with AI-generated questions</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Topic Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              <BookOpen className="w-4 h-4 inline mr-2" />
              Select Topic
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {topics.map((topicOption) => (
                <motion.button
                  key={topicOption}
                  type="button"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setTopic(topicOption)}
                  className={`p-3 text-sm font-medium rounded-lg border-2 transition-all ${
                    topic === topicOption
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  {topicOption}
                </motion.button>
              ))}
            </div>
            {!topic && (
              <p className="text-sm text-gray-500 mt-2">Please select a topic to continue</p>
            )}
          </div>

          {/* Difficulty Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              <Target className="w-4 h-4 inline mr-2" />
              Difficulty Level
            </label>
            <div className="space-y-3">
              {difficulties.map((diff) => (
                <motion.label
                  key={diff.value}
                  whileHover={{ scale: 1.01 }}
                  className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    difficulty === diff.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="difficulty"
                    value={diff.value}
                    checked={difficulty === diff.value}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="sr-only"
                  />
                  <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                    difficulty === diff.value ? 'border-primary-500 bg-primary-500' : 'border-gray-300'
                  }`}>
                    {difficulty === diff.value && (
                      <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className={`font-medium ${diff.color}`}>{diff.label}</span>
                    </div>
                    <p className="text-sm text-gray-600">{diff.description}</p>
                  </div>
                </motion.label>
              ))}
            </div>
          </div>

          {/* Number of Questions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              <Clock className="w-4 h-4 inline mr-2" />
              Number of Questions
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="3"
                max="15"
                value={numQuestions}
                onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex items-center justify-center w-16 h-10 bg-primary-100 text-primary-700 font-bold rounded-lg">
                {numQuestions}
              </div>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>3 questions</span>
              <span>15 questions</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Estimated time: {Math.ceil(numQuestions * 1.5)} minutes
            </p>
          </div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={!topic || isLoading}
            whileHover={{ scale: topic ? 1.02 : 1 }}
            whileTap={{ scale: topic ? 0.98 : 1 }}
            className="w-full bg-primary-600 text-white py-4 px-6 rounded-lg font-medium hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Generating Quiz...</span>
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                <span>Generate Quiz</span>
              </>
            )}
          </motion.button>
        </form>

        {/* Features */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div className="p-4">
              <Brain className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">AI-Powered</h3>
              <p className="text-sm text-gray-600">Questions generated by IBM Granite AI</p>
            </div>
            <div className="p-4">
              <Target className="w-8 h-8 text-success-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Adaptive</h3>
              <p className="text-sm text-gray-600">Difficulty adjusts to your level</p>
            </div>
            <div className="p-4">
              <Clock className="w-8 h-8 text-warning-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Instant Feedback</h3>
              <p className="text-sm text-gray-600">Get results immediately</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default QuizSetup;