import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import ConvertibleBondsBacktest from './pages/ConvertibleBondsBacktest';
import './App.css';

function PrivateRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/login" element={
            <Login />
          } />
          <Route path="/register" element={
            <Register />
          } />
          <Route path="/backtest" element={
            <PrivateRoute>
              <ConvertibleBondsBacktest />
            </PrivateRoute>
          } />
          <Route path="/" element={
            <Navigate to="/login" replace />
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;