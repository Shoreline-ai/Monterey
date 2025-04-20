import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FaUser, FaLock, FaEnvelope } from 'react-icons/fa';
import AuthCard from '../components/AuthCard';
import api from '../utils/axios';
import { config } from '../config';

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.post('/api/register', {
        username: formData.username,
        email: formData.email,
        password: formData.password
      });

      alert('Registration successful! Please login.');
      navigate('/login');
    } catch (error) {
      setError(error.response?.data?.message || 'Error registering user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title={
        <div className="flex flex-col items-center mb-6">
          {/* 🧠 Big brand title inside the card */}
          <h1 className="text-2xl sm:text-3xl font-extrabold text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-pink-400 drop-shadow-sm mb-3">
            {config.appName}
          </h1>
          
          {/* Smaller login section title */}
          <h2 className="text-2xl font-bold text-blue-300">Create your account</h2>
        </div>
      }
      subtitle="Start exploring convertible bond strategies"
      footer={
        <>
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:underline">Sign in</Link>
        </>
      }
    >
      {error && (
        <div className="bg-red-500/10 border border-red-500 text-red-400 p-3 rounded text-sm">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input icon={<FaUser />} name="username" placeholder="Username" value={formData.username} onChange={handleChange} />
        <Input icon={<FaEnvelope />} name="email" placeholder="Email" type="email" value={formData.email} onChange={handleChange} />
        <Input icon={<FaLock />} name="password" placeholder="Password" type="password" value={formData.password} onChange={handleChange} />
        <Input icon={<FaLock />} name="confirmPassword" placeholder="Confirm Password" type="password" value={formData.confirmPassword} onChange={handleChange} />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 transition py-3 rounded-md font-semibold shadow-md flex items-center justify-center"
        >
          {loading ? <span className="loader mr-2"></span> : null}
          Create Account
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
