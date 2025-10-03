import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-slate-800 mb-4">Refsan Türkiye</h1>
        <p className="text-lg text-slate-600 mb-8">Seramik Makineleri Teknik Servis</p>
        <div className="space-y-4">
          <button 
            data-testid="demo-admin-btn"
            className="block w-full px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700"
            onClick={() => alert('Admin demo')}
          >
            Admin Demo
          </button>
          <button 
            data-testid="demo-technician-btn"
            className="block w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            onClick={() => alert('Teknisyen demo')}
          >
            Teknisyen Demo
          </button>
          <button 
            data-testid="demo-customer-btn"
            className="block w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            onClick={() => alert('Müşteri demo')}
          >
            Müşteri Demo
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;