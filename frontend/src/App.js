import { useState } from "react";
import Header from "./components/Header";
import CodeEditor from "./components/CodeEditor";
import ResultPanel from "./components/ResultPanel";
import { analyzeCode } from "./api/analyze";

// ── Example test cases ──
const EXAMPLES = [
  {
    label: "O(n²) Nested Loop",
    language: "python",
    code: `def find_pairs(arr, target):
    result = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i] + arr[j] == target:
                result.append((i, j))
    return result`,
  },
  {
    label: "O(2ⁿ) Fibonacci",
    language: "python",
    code: `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)`,
  },
  {
    label: "String Concat Bug",
    language: "python",
    code: `def build_string(words):
    result = ""
    for word in words:
        result += word + ", "
    return result`,
  },
  {
    label: "Clean O(n)",
    language: "python",
    code: `def find_max(arr):
    max_val = arr[0]
    for item in arr:
        if item > max_val:
            max_val = item
    return max_val`,
  },
];

const App = () => {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async () => {
    setResult(null);
    setError(null);
    setIsLoading(true);
    const { data, error: apiError } = await analyzeCode(code, language);
    if (apiError) setError(apiError);
    else setResult(data);
    setIsLoading(false);
  };

  const loadExample = (example) => {
    setCode(example.code);
    setLanguage(example.language);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-6xl mx-auto px-4 pb-16">
        <Header />

        {/* ── Example buttons ── */}
        <div
          className="mt-6 flex flex-wrap gap-2 
                        justify-center"
        >
          <span
            className="text-gray-500 text-sm 
                           self-center mr-1"
          >
            Try:
          </span>
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => loadExample(ex)}
              className="px-3 py-1.5 text-xs rounded-lg
                         bg-gray-800 hover:bg-gray-700
                         text-gray-300 hover:text-white
                         border border-gray-700
                         transition-colors duration-150"
            >
              {ex.label}
            </button>
          ))}
        </div>

        {/* ── Main layout ── */}
        <div
          className="mt-6 grid grid-cols-1 
                        lg:grid-cols-2 gap-8"
        >
          <div
            className="bg-gray-900 rounded-2xl border 
                          border-gray-800 p-6 shadow-xl"
          >
            <h2
              className="text-gray-400 text-sm font-semibold 
                           uppercase tracking-widest mb-4"
            >
              📝 Input Code
            </h2>
            <CodeEditor
              code={code}
              language={language}
              onCodeChange={setCode}
              onLanguageChange={setLanguage}
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
            />
          </div>

          <div
            className="bg-gray-900 rounded-2xl border 
                          border-gray-800 p-6 shadow-xl"
          >
            <h2
              className="text-gray-400 text-sm font-semibold 
                           uppercase tracking-widest mb-4"
            >
              📊 Analysis Results
            </h2>
            <ResultPanel
              result={result}
              error={error}
              code={code}
              language={language}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
