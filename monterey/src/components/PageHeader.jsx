import { useNavigate } from 'react-router-dom';

export default function PageHeader() {
  const username = localStorage.getItem('username');
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <div className="flex items-center justify-between mb-6 px-2">
          {/* 🧠 Big brand title inside the card */}
          <h1 className="text-2xl sm:text-3xl font-extrabold text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-pink-400 drop-shadow-sm mb-3">
            Convertible Bond Backtest
          </h1>
       <div className="flex items-center gap-4 text-sm text-gray-300">
        <span>Welcome, <span className="font-semibold">{username}</span></span>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-md text-sm font-medium"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
