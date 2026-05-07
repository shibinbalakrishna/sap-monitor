import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

const App = () => {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Check backend API status
    fetch(`${process.env.REACT_APP_API_URL}/health`)
      .then(res => res.json())
      .then(data => setApiStatus('connected'))
      .catch(err => {
        console.error('API connection error:', err);
        setApiStatus('disconnected');
      });
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-blue-600">SAP Monitor</h1>
              </div>
              <div className="flex items-center space-x-4">
                <Link to="/" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
                <Link to="/servers" className="text-gray-600 hover:text-gray-900">Servers</Link>
                <Link to="/alerts" className="text-gray-600 hover:text-gray-900">Alerts</Link>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  apiStatus === 'connected' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {apiStatus}
                </span>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">Dashboard</h2>
                <p>SAP Infrastructure Monitoring Platform - Under Development</p>
              </div>
            } />
            <Route path="/servers" element={
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">Servers</h2>
                <p>Server management interface - Under Development</p>
              </div>
            } />
            <Route path="/alerts" element={
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">Alerts</h2>
                <p>Alert management - Under Development</p>
              </div>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
