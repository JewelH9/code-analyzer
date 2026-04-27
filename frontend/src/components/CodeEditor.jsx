// CodeEditor.jsx
// Responsibility: Accept user input (code + language)
// and trigger analysis.

const PLACEHOLDER = {
  python: `# Paste your Python code here
def find_pairs(arr, target):
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i] + arr[j] == target:
                print(i, j)`,

  cpp: `// Paste your C++ code here
void findPairs(int arr[], int n, int target) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (arr[i] + arr[j] == target)
                cout << i << " " << j;
        }
    }
}`,
};

const CodeEditor = ({
  code,
  language,
  onCodeChange,
  onLanguageChange,
  onAnalyze,
  isLoading,
}) => {
  return (
    <div className="flex flex-col gap-4">
      {/* ── Top bar: language selector ── */}
      <div className="flex items-center justify-between">
        <label className="text-gray-400 text-sm font-medium">Language</label>
        <select
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
          className="bg-gray-800 text-white border border-gray-700 
                     rounded-lg px-3 py-1.5 text-sm
                     focus:outline-none focus:border-blue-500"
        >
          <option value="python">Python</option>
          <option value="cpp">C++</option>
        </select>
      </div>

      {/* ── Code textarea ── */}
      <div className="relative">
        <textarea
          value={code}
          onChange={(e) => onCodeChange(e.target.value)}
          placeholder={PLACEHOLDER[language]}
          spellCheck={false}
          className="w-full h-72 bg-gray-900 text-green-400 
                     font-mono text-sm
                     border border-gray-700 rounded-xl p-4
                     focus:outline-none focus:border-blue-500
                     resize-none placeholder-gray-600
                     leading-relaxed"
        />
        {/* character count */}
        <span
          className="absolute bottom-3 right-3 
                         text-gray-600 text-xs"
        >
          {code.length} chars
        </span>
      </div>

      {/* ── Analyze button ── */}
      <button
        onClick={onAnalyze}
        disabled={isLoading || !code.trim()}
        className={`w-full py-3 rounded-xl font-semibold text-base
                    transition-all duration-200
                    ${
                      isLoading || !code.trim()
                        ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                        : "bg-blue-600 hover:bg-blue-500 text-white cursor-pointer shadow-lg hover:shadow-blue-500/25"
                    }`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg
              className="animate-spin h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8z"
              />
            </svg>
            Analyzing...
          </span>
        ) : (
          "⚡ Analyze Code"
        )}
      </button>
    </div>
  );
};

export default CodeEditor;
