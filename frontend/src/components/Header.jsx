// Header.jsx — Simple, clean top bar

const Header = () => {
  return (
    <div className="text-center py-8 border-b border-gray-800">
      <h1 className="text-4xl font-bold text-white tracking-tight">
        ⚡ Code Performance Analyzer
      </h1>
      <p className="text-gray-400 mt-2 text-lg">
        Paste your code → Get complexity analysis + optimization tips
      </p>
      <div className="flex justify-center gap-3 mt-4">
        <span
          className="px-3 py-1 bg-blue-900 text-blue-300 
                         rounded-full text-sm"
        >
          Python
        </span>
        <span
          className="px-3 py-1 bg-orange-900 text-orange-300 
                         rounded-full text-sm"
        >
          C++
        </span>
        <span
          className="px-3 py-1 bg-green-900 text-green-300 
                         rounded-full text-sm"
        >
          Rule-Based + AST
        </span>
      </div>
    </div>
  );
};

export default Header;
