export default function JsonDisplay({ json }) {
    const handleCopy = () => {
      navigator.clipboard.writeText(JSON.stringify(json, null, 2));
      alert('Configuration copied to clipboard!');
    };
  
    return (
      <div className="bg-white/5 text-gray-200 p-4 rounded-lg border border-gray-700 relative mt-8">
        <button
          onClick={handleCopy}
          className="absolute top-2 right-3 px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded-md"
        >
          Copy
        </button>
        <pre className="text-sm whitespace-pre-wrap break-all">
          {JSON.stringify(json, null, 2)}
        </pre>
      </div>
    );
  }
  