import { Link } from 'react-router-dom';
import logo from '../assets/react.svg'; // 或用字体图标代替

export default function AuthCard({ title, subtitle, children, footer }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 px-4">
      <div className="backdrop-blur-md bg-[#1e1e2f]/80 border border-gray-700 text-white p-8 rounded-xl shadow-2xl w-full max-w-md space-y-6">
        <div className="text-center">
          <img src={logo} alt="logo" className="h-10 mx-auto mb-4" />
          <h1 className="text-3xl font-bold tracking-tight text-blue-400">{title}</h1>
          <p className="mt-1 text-sm text-gray-400">{subtitle}</p>
        </div>
        {children}
        <div className="text-sm text-center text-gray-500">{footer}</div>
      </div>
    </div>
  );
}
