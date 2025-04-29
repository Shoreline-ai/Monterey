import { Link } from 'react-router-dom';
import logo from '../assets/react.svg'; // 或用字体图标代替
import Footer from './Footer';

export default function AuthCard({ title, subtitle, children, footer }) {
  return (
    <div className="w-screen min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 px-6">
      <div className="backdrop-blur-md bg-[#1e1e2f]/80 border border-gray-700 text-white p-10 rounded-xl shadow-2xl w-full max-w-xl space-y-8">
        <div className="text-center">
          <img src={logo} alt="logo" className="h-14 mx-auto mb-6" />
          <h1 className="text-4xl font-bold tracking-tight text-blue-400">{title}</h1>
          <p className="mt-2 text-base text-gray-400">{subtitle}</p>
        </div>
        <div className="py-4">
          {children}
        </div>
        <div className="text-base text-center text-gray-500 pt-4">{footer}</div>
      </div>
      <div className="mt-8 w-full max-w-xl">
        <Footer />
      </div>
    </div>
  );
}
