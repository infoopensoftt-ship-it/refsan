import React from 'react';
import HtmlRedirect from './HtmlRedirect';
import './App.css';

// Removed complex React components to fix hook errors

// Main App Component - Simplified to redirect to HTML files
function App() {
  return <HtmlRedirect />;
}

// Dashboard Router based on user role
const DashboardRouter = () => {
  const { user } = useAuth();
  
  if (!user) return <Navigate to="/login" replace />;
  
  switch (user.role) {
    case 'admin':
      return <Navigate to="/admin" replace />;
    case 'teknisyen':
      return <Navigate to="/teknisyen" replace />;
    case 'musteri':
      return <Navigate to="/musteri" replace />;
    default:
      return <Navigate to="/login" replace />;
  }
};

export default App;