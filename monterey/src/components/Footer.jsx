import { FaXTwitter, FaInstagram, FaYoutube } from 'react-icons/fa6';

export default function Footer() {
  return (
    <div className="w-full backdrop-blur-md bg-[#1e1e2f]/80 border border-gray-700 p-8 rounded-xl shadow-2xl">
      <div className="flex justify-center space-x-6">
        <a 
          href="https://x.com/convertedbond" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-blue-400 transition-colors"
        >
          <FaXTwitter className="w-6 h-6" />
        </a>
        <a 
          href="https://instagram.com/convertedbond" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-blue-400 transition-colors"
        >
          <FaInstagram className="w-6 h-6" />
        </a>
        <a 
          href="https://youtube.com/@convertedbond" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-blue-400 transition-colors"
        >
          <FaYoutube className="w-6 h-6" />
        </a>
      </div>
      <div className="mt-4 text-center text-sm text-gray-400">
        <p>Copyright © {new Date().getFullYear()} - All rights reserved by Convertible Bond</p>
      </div>
    </div>
  );
}