import { useState } from "react";

// Individual suggestion card with expandable before/after
const SuggestionCard = ({ suggestion, index }) => {
  const [expanded, setExpanded] = useState(false);
  const isGood = suggestion.title.startsWith("✅");

  return (
    <li
      className={`rounded-xl border text-sm
                    ${
                      isGood
                        ? "border-green-800 bg-green-900/20"
                        : "border-blue-900 bg-blue-900/10"
                    }`}
    >
      {/* ── Header ── */}
      <div
        className="flex items-start justify-between 
                   p-3 cursor-pointer"
        onClick={() => !isGood && setExpanded(!expanded)}
      >
        <div className="flex gap-2">
          <span
            className="text-blue-400 font-bold 
                           min-w-[20px]"
          >
            {isGood ? "" : `${index + 1}.`}
          </span>
          <div>
            <div
              className={`font-semibold 
                             ${isGood ? "text-green-300" : "text-blue-200"}`}
            >
              {suggestion.title}
            </div>
            <div className="text-gray-400 text-xs mt-0.5">
              {suggestion.detail}
            </div>
          </div>
        </div>

        {/* Complexity gain badge */}
        {suggestion.complexity_gain && (
          <span
            className="text-xs bg-purple-900/50 
                           text-purple-300 px-2 py-1 
                           rounded-full whitespace-nowrap ml-2"
          >
            {suggestion.complexity_gain}
          </span>
        )}
      </div>

      {/* ── Expandable before/after ── */}
      {!isGood && suggestion.before && expanded && (
        <div className="px-3 pb-3 grid grid-cols-2 gap-2">
          <div>
            <div
              className="text-xs text-red-400 
                            font-semibold mb-1"
            >
              ❌ Before
            </div>
            <pre
              className="bg-gray-950 text-red-300 
                            text-xs rounded-lg p-2 
                            overflow-x-auto whitespace-pre-wrap"
            >
              {suggestion.before}
            </pre>
          </div>
          <div>
            <div
              className="text-xs text-green-400 
                            font-semibold mb-1"
            >
              ✅ After
            </div>
            <pre
              className="bg-gray-950 text-green-300 
                            text-xs rounded-lg p-2 
                            overflow-x-auto whitespace-pre-wrap"
            >
              {suggestion.after}
            </pre>
          </div>
        </div>
      )}

      {/* expand hint */}
      {!isGood && suggestion.before && (
        <div
          className="text-center text-gray-600 
                        text-xs pb-2 cursor-pointer"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "▲ hide example" : "▼ show example"}
        </div>
      )}
    </li>
  );
};

const SuggestionsList = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div
      className="rounded-xl border border-gray-700 
                    bg-gray-900 p-4"
    >
      <h3
        className="text-sm font-semibold text-gray-400 
                     uppercase tracking-widest mb-3"
      >
        💡 Optimization Suggestions
      </h3>
      <ul className="flex flex-col gap-2">
        {suggestions.map((s, i) => (
          <SuggestionCard key={i} suggestion={s} index={i} />
        ))}
      </ul>
    </div>
  );
};

export default SuggestionsList;
