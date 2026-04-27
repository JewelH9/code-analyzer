// ResultPanel.jsx
// Assembles all result components into one panel.

import ComplexityBadge from "./ComplexityBadge";
import IssuesList from "./IssuesList";
import SuggestionsList from "./SuggestionsList";

const ResultPanel = ({ result, error }) => {
  // ── Error state ──
  if (error) {
    return (
      <div
        className="rounded-xl border border-red-800 
                      bg-red-900/20 p-6 text-red-400 text-sm"
      >
        <div className="font-bold mb-1">❌ Error</div>
        <div>{error}</div>
      </div>
    );
  }

  // ── Empty state ──
  if (!result) {
    return (
      <div
        className="rounded-xl border border-gray-800 
                      bg-gray-900/50 p-8
                      flex flex-col items-center 
                      justify-center text-center gap-3"
      >
        <div className="text-4xl">🔬</div>
        <div className="text-gray-500 text-sm">
          Paste your code and click{" "}
          <strong className="text-gray-400">Analyze</strong> to see results
        </div>
      </div>
    );
  }

  // ── Results state ──
  return (
    <div className="flex flex-col gap-4">
      <ComplexityBadge complexity={result.time_complexity} />
      <IssuesList issues={result.issues} />
      <SuggestionsList suggestions={result.suggestions} />
    </div>
  );
};

export default ResultPanel;
