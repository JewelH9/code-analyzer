const getColor = (label) => {
  if (!label) return "gray";
  if (label.includes("2ⁿ") || label.includes("n³")) return "red";
  if (label.includes("n²")) return "orange";
  if (label.includes("log")) return "yellow";
  if (label.includes("O(n)")) return "yellow";
  if (label.includes("O(1)")) return "green";
  return "blue";
};

const COLOR = {
  red: "bg-red-900/40 text-red-300 border-red-700",
  orange: "bg-orange-900/40 text-orange-300 border-orange-700",
  yellow: "bg-yellow-900/40 text-yellow-300 border-yellow-700",
  green: "bg-green-900/40 text-green-300 border-green-700",
  blue: "bg-blue-900/40 text-blue-300 border-blue-700",
  gray: "bg-gray-800 text-gray-300 border-gray-600",
};

const CONFIDENCE_COLOR = {
  high: "text-green-400",
  medium: "text-yellow-400",
  low: "text-red-400",
};

const ComplexityBadge = ({ complexity }) => {
  if (!complexity) return null;

  const color = getColor(complexity.label);

  return (
    <div className={`rounded-xl border p-5 ${COLOR[color]}`}>
      {/* ── Top row ── */}
      <div className="flex items-start justify-between">
        <div>
          <div
            className="text-xs uppercase tracking-widest 
                          opacity-60 mb-1"
          >
            Time Complexity
          </div>
          <div className="text-3xl font-bold font-mono">{complexity.label}</div>
        </div>

        {/* Confidence pill */}
        <span
          className={`text-xs font-semibold px-2 py-1 
                          rounded-full bg-black/20
                          ${CONFIDENCE_COLOR[complexity.confidence]}`}
        >
          {complexity.confidence} confidence
        </span>
      </div>

      {/* ── Reason ── */}
      {complexity.reason && (
        <div
          className="mt-3 text-xs opacity-70 border-t 
                        border-current/20 pt-3"
        >
          📌 {complexity.reason}
        </div>
      )}
    </div>
  );
};

export default ComplexityBadge;
