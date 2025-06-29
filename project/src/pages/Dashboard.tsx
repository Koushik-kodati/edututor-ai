import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import StudentDashboard from '../components/Dashboard/StudentDashboard';
import EducatorDashboard from '../components/Dashboard/EducatorDashboard';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <div>Loading...</div>;
  }

  return user.role === 'educator' ? <EducatorDashboard /> : <StudentDashboard />;
};

export default Dashboard;