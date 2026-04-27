# suggester.py (upgraded)
# Now has TWO layers:
#   Layer 1: Issue-based suggestions (reactive)
#   Layer 2: Code pattern suggestions (proactive)

import re

# ─────────────────────────────────────────────────────────────
# LAYER 1: Issue → Suggestion mapping
# ─────────────────────────────────────────────────────────────
ISSUE_RULES = [
    {
        "trigger":    "nested loop",
        "title":      "Replace Nested Loop with HashMap",
        "detail":     "A nested loop checking pairs costs O(n²). "
                      "Store values in a dict for O(1) lookup.",
        "before":     "for i in range(n):\n"
                      "    for j in range(n):\n"
                      "        if arr[i]+arr[j]==target: ...",
        "after":      "seen = {}\n"
                      "for i, val in enumerate(arr):\n"
                      "    if target-val in seen: ...\n"
                      "    seen[val] = i",
        "complexity_gain": "O(n²) → O(n)"
    },
    {
        "trigger":    "len()",
        "title":      "Cache len() Outside Loop",
        "detail":     "len() is O(1) in Python but calling it n times "
                      "adds unnecessary overhead and signals poor practice.",
        "before":     "for i in range(len(arr)): ...",
        "after":      "n = len(arr)\nfor i in range(n): ...",
        "complexity_gain": "Cleaner + avoids repeated calls"
    },
    {
        "trigger":    "sorted()",
        "title":      "Sort Once, Not Per Iteration",
        "detail":     "sorted() is O(n log n). Inside a loop = O(n² log n).",
        "before":     "for x in data:\n    s = sorted(data)\n    ...",
        "after":      "s = sorted(data)\nfor x in data:\n    ...",
        "complexity_gain": "O(n² log n) → O(n log n)"
    },
    {
        "trigger":    "sum()",
        "title":      "Use Running Total Instead of sum()",
        "detail":     "Calling sum() inside a loop recalculates "
                      "the entire list each iteration.",
        "before":     "for i in range(n):\n    total = sum(arr[:i])",
        "after":      "total = 0\nfor val in arr:\n    total += val",
        "complexity_gain": "O(n²) → O(n)"
    },
    {
        "trigger":    "string concatenation",
        "title":      "Use list + join() for String Building",
        "detail":     "Strings are immutable in Python. "
                      "+= creates a new object every iteration → O(n²) memory.",
        "before":     "result = ''\nfor w in words:\n    result += w",
        "after":      "parts = []\nfor w in words:\n    parts.append(w)\n"
                      "result = ''.join(parts)",
        "complexity_gain": "O(n²) memory → O(n)"
    },
    {
        "trigger":    "recursive function",
        "title":      "Add Memoization to Recursion",
        "detail":     "Without memoization, recursive functions "
                      "recompute the same subproblems repeatedly.",
        "before":     "def fib(n):\n    return fib(n-1) + fib(n-2)",
        "after":      "from functools import lru_cache\n"
                      "@lru_cache(maxsize=None)\n"
                      "def fib(n):\n    return fib(n-1) + fib(n-2)",
        "complexity_gain": "O(2ⁿ) → O(n)"
    },
    {
        "trigger":    "exponential",
        "title":      "Convert Recursion to Dynamic Programming",
        "detail":     "Bottom-up DP eliminates recursion overhead "
                      "and stack overflow risk entirely.",
        "before":     "def fib(n):\n    return fib(n-1) + fib(n-2)",
        "after":      "def fib(n):\n    dp = [0, 1]\n"
                      "    for i in range(2, n+1):\n"
                      "        dp.append(dp[-1] + dp[-2])\n"
                      "    return dp[n]",
        "complexity_gain": "O(2ⁿ) → O(n) time, O(n) space"
    },
]

# ─────────────────────────────────────────────────────────────
# LAYER 2: Proactive pattern detection in raw code
# These fire even if no "issue" was detected
# ─────────────────────────────────────────────────────────────
PROACTIVE_RULES = [
    {
        # Detects: if x in some_list (linear search)
        # Suggest: use a set for O(1) lookup
        "pattern":   re.compile(r'\bif\s+\w+\s+in\s+\w+'),
        "title":     "Use set() for Membership Testing",
        "detail":    "'if x in list' is O(n). "
                     "Convert to set for O(1) lookup.",
        "before":    "my_list = [1,2,3]\nif x in my_list: ...",
        "after":     "my_set = {1,2,3}\nif x in my_set: ...",
        "complexity_gain": "O(n) → O(1) lookup"
    },
    {
        # Detects: list.append inside loop without list comprehension
        "pattern":   re.compile(
                        r'for\s+\w+\s+in\s+.*:\s*\n\s+\w+\.append\('
                     ),
        "title":     "Consider List Comprehension",
        "detail":    "List comprehensions are faster than "
                     "append() in a loop (optimized at C level).",
        "before":    "result = []\nfor x in data:\n    result.append(x*2)",
        "after":     "result = [x*2 for x in data]",
        "complexity_gain": "Same O(n) but ~30% faster in practice"
    },
    {
        # Detects: dict access inside loop without .get()
        "pattern":   re.compile(r'\w+\[\w+\]\s*=\s*\w+\[\w+\]\s*\+\s*1'),
        "title":     "Use collections.defaultdict or dict.get()",
        "detail":    "Direct dict[key] += 1 crashes if key missing. "
                     "Use defaultdict or .get() with default.",
        "before":    "count[x] = count[x] + 1  # KeyError if x missing",
        "after":     "from collections import defaultdict\n"
                     "count = defaultdict(int)\ncount[x] += 1",
        "complexity_gain": "Safer + cleaner code"
    },
]


def generate_suggestions(issues: list, parsed: dict = None) -> list:
    """
    Layer 1: Match issues to suggestion rules.
    Layer 2: Scan code directly for proactive patterns.
    """
    suggestions = []
    seen_titles = set()

    # ── Layer 1: Issue-based ──
    for issue in issues:
        for rule in ISSUE_RULES:
            if rule["trigger"].lower() in issue.lower():
                if rule["title"] not in seen_titles:
                    suggestions.append(_format_suggestion(rule))
                    seen_titles.add(rule["title"])

    # ── Layer 2: Proactive (if parsed data available) ──
    if parsed:
        code = parsed.get("raw_code", "")
        for rule in PROACTIVE_RULES:
            if rule["pattern"].search(code):
                if rule["title"] not in seen_titles:
                    suggestions.append(_format_suggestion(rule))
                    seen_titles.add(rule["title"])

    if not suggestions:
        suggestions.append({
            "title":            "✅ Code Looks Efficient!",
            "detail":           "No major performance issues detected.",
            "before":           None,
            "after":            None,
            "complexity_gain":  None
        })

    return suggestions


def _format_suggestion(rule: dict) -> dict:
    """
    Return suggestion as a structured dict
    (not just a string like before).
    Richer data → richer UI.
    """
    return {
        "title":           rule["title"],
        "detail":          rule["detail"],
        "before":          rule.get("before"),
        "after":           rule.get("after"),
        "complexity_gain": rule.get("complexity_gain")
    }