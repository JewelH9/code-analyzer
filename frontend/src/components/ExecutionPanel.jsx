// ExecutionPanel.jsx
// Runs code and shows output + timing

import { useState } from "react";
import axios from "axios";

const ExecutionPanel = ({ code, language }) => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRun = async () => {
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";
      const res = await axios.post(`${BASE_URL}/execute`, {
        code,
        language,
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || "Execution failed");
    }

    setLoading(false);
  };

  return (
    <div
      className="rounded-xl border border-gray-700 
                    bg-gray-900 p-4 mt-4"
    >
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-3">
        <h3
          className="text-sm font-semibold text-gray-400 
                       uppercase tracking-widest"
        >
          ▶ Run Code
        </h3>
        <button
          onClick={handleRun}
          disabled={loading || !code.trim()}
          className={`px-4 py-1.5 rounded-lg text-sm font-semibold
                      transition-all duration-150
                      ${
                        loading || !code.trim()
                          ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                          : "bg-green-700 hover:bg-green-600 text-white"
                      }`}
        >
          {loading ? "⏳ Running..." : "▶ Run"}
        </button>
      </div>

      {/* ── Result ── */}
      {result && (
        <div className="space-y-2">
          {/* Timing badge */}
          {result.exec_time_ms && (
            <div className="flex gap-2 items-center">
              <span className="text-xs text-gray-500">Execution time:</span>
              <span
                className="text-xs font-mono font-bold 
                               text-green-400 bg-green-900/30 
                               px-2 py-0.5 rounded-full"
              >
                ⏱ {result.exec_time_ms.toFixed(2)} ms
              </span>
            </div>
          )}

          {/* Output */}
          <pre
            className={`text-xs font-mono rounded-lg p-3 
                           overflow-x-auto whitespace-pre-wrap
                           max-h-48 overflow-y-auto
                           ${
                             result.success
                               ? "bg-gray-950 text-green-300"
                               : "bg-red-950 text-red-300"
                           }`}
          >
            {result.output || result.error || "No output"}
          </pre>

          {/* Timeout warning */}
          {result.timed_out && (
            <div
              className="text-xs text-red-400 
                            bg-red-900/20 rounded-lg p-2"
            >
              ⚠️ Code exceeded {5}s time limit and was killed. Check for
              infinite loops.
            </div>
          )}

          {/* Blocked warning */}
          {result.blocked && (
            <div
              className="text-xs text-orange-400 
                            bg-orange-900/20 rounded-lg p-2"
            >
              ⛔ Execution blocked for security reasons.
            </div>
          )}
        </div>
      )}

      {error && <div className="text-xs text-red-400 mt-2">{error}</div>}
    </div>
  );
};

export default ExecutionPanel;
