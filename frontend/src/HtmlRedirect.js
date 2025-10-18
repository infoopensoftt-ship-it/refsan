import React, { useEffect } from 'react';

const HtmlRedirect = () => {
  useEffect(() => {
    // Check if user has a token in localStorage
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      try {
        const userData = JSON.parse(user);
        // Redirect based on user role
        switch(userData.role) {
          case 'admin':
            window.location.replace('/admin.html');
            break;
          case 'teknisyen':
            window.location.replace('/teknisyen.html');
            break;
          case 'musteri':
            window.location.replace('/musteri.html');
            break;
          default:
            window.location.replace('/test.html');
        }
      } catch (e) {
        // If error parsing user data, go to login
        window.location.replace('/test.html');
      }
    } else {
      // No token, redirect to login page
      window.location.replace('/test.html');
    }
  }, []);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h2 style={{ color: '#f97316' }}>🔧 Refsan Technical Türkiye</h2>
        <p>Yönlendiriliyor...</p>
      </div>
    </div>
  );
};

export default HtmlRedirect;