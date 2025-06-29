import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/Auth/LoginForm';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Quiz from './pages/Quiz';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return user ? <>{children}</> : <Navigate to="/login" />;
};

const AppRoutes: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <LoginForm />;
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/history" element={<div className="p-8 text-center text-gray-600">Quiz History - Coming Soon</div>} />
        <Route path="/courses" element={<div className="p-8 text-center text-gray-600">Courses - Coming Soon</div>} />
        <Route path="/achievements" element={<div className="p-8 text-center text-gray-600">Achievements - Coming Soon</div>} />
        <Route path="/students" element={<div className="p-8 text-center text-gray-600">Students Management - Coming Soon</div>} />
        <Route path="/analytics" element={<div className="p-8 text-center text-gray-600">Analytics - Coming Soon</div>} />
        <Route path="/settings" element={<div className="p-8 text-center text-gray-600">Settings - Coming Soon</div>} />
      </Routes>
    </Layout>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppRoutes />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;