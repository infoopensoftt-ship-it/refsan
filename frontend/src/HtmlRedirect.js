import React, { useEffect } from 'react';

const HtmlRedirect = () => {
  useEffect(() => {
    // Redirect to the HTML login page
    window.location.href = '/test.html';
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
        <h2>🔧 Refsan Türkiye</h2>
        <p>Redirecting to login page...</p>
        <p><a href="/test.html">Click here if not redirected automatically</a></p>
      </div>
    </div>
  );
};

export default HtmlRedirect;