import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FaUser, FaLock } from 'react-icons/fa';
import AuthCard from '../components/AuthCard';
import api from '../utils/axios';
import { config } from '../config';

export default function Login() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    // Clear error when user starts typing
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate empty fields
    if (!formData.username.trim() || !formData.password.trim()) {
      setError('Username and password are required');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await api.post('/api/login', formData);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('username', response.data.username);
      navigate('/backtest');
    } catch (error) {
      setError(error.response?.data?.message || 'Error logging in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title={
        <div className="flex flex-col items-center mb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-pink-400 drop-shadow-sm mb-3">
            {config.appName}
          </h1>
          
          <h2 className="text-2xl font-bold text-blue-300">Welcome Back</h2>
        </div>
      }
      subtitle="Log in to manage your strategies"
      footer={
        <>
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-400 hover:underline">Sign up</Link>
        </>
      }
    >
      {error && (
        <div className="bg-red-500/10 border border-red-500 text-red-400 p-3 rounded text-sm mb-4">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          icon={<FaUser />}
          name="username"
          placeholder="Username"
          value={formData.username}
          onChange={handleChange}
          required
          aria-required="true"
        />
        <Input
          icon={<FaLock />}
          name="password"
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
          aria-required="true"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 transition py-3 rounded-md font-semibold shadow-md flex items-center justify-center"
        >
          {loading ? <span className="loader mr-2"></span> : null}
          Log In
        </button>
      </form>
    </AuthCard>
  );
}

function Input({ icon, ...props }) {
  return (
    <div className="relative">
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</span>
      <input
        {...props}
        className="w-full px-10 py-3 rounded-md bg-gray-800 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
      />
    </div>
  );
}
