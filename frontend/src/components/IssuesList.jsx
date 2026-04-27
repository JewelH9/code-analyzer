// IssuesList.jsx — Displays detected issues

const IssuesList = ({ issues }) => {
  if (!issues || issues.length === 0) return null;

  const allGood = issues.length === 1 && issues[0].startsWith("✅");

  return (
    <div
      className="rounded-xl border border-gray-700 
                    bg-gray-900 p-4"
    >
      <h3
        className="text-sm font-semibold text-gray-400 
                     uppercase tracking-widest mb-3"
      >
        🔍 Detected Issues
      </h3>
      <ul className="flex flex-col gap-2">
        {issues.map((issue, idx) => (
          <li
            key={idx}
            className={`text-sm rounded-lg px-3 py-2 
                        font-mono leading-relaxed
                        ${
                          allGood
                            ? "bg-green-900/30 text-green-300"
                            : "bg-red-900/20 text-red-300"
                        }`}
          >
            {issue}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default IssuesList;
