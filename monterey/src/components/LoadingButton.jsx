export default function LoadingButton({ isLoading, children, ...props }) {
    return (
      <button
        {...props}
        disabled={isLoading}
        className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-md font-semibold 
          ${isLoading ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-500'} 
          text-white transition`}
      >
        {isLoading && (
          <span className="loader w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        )}
        {children}
      </button>
    );
}
  