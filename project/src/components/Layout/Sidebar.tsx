import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Home, 
  Brain, 
  History, 
  Users, 
  BarChart3, 
  Settings,
  BookOpen,
  Trophy
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const studentNavItems = [
    { to: '/dashboard', icon: Home, label: 'Dashboard' },
    { to: '/quiz', icon: Brain, label: 'Take Quiz' },
    { to: '/history', icon: History, label: 'Quiz History' },
    { to: '/courses', icon: BookOpen, label: 'My Courses' },
    { to: '/achievements', icon: Trophy, label: 'Achievements' },
  ];

  const educatorNavItems = [
    { to: '/dashboard', icon: Home, label: 'Dashboard' },
    { to: '/students', icon: Users, label: 'Students' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/courses', icon: BookOpen, label: 'Courses' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ];

  const navItems = user?.role === 'educator' ? educatorNavItems : studentNavItems;

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen">
      <nav className="mt-8 px-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;