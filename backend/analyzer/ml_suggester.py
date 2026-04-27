# ml_suggester.py
# Lightweight ML suggestion engine using TF-IDF similarity.
#
# Why TF-IDF?
# - No GPU needed
# - No model download
# - Works on small datasets
# - Fast (milliseconds)
# - Explainable (you can show WHY it matched)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ─────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# Each entry: code snippet that represents a problem pattern
# + the suggestion for that pattern
# ─────────────────────────────────────────────────────────
KNOWLEDGE_BASE = [
    {
        "pattern_code": """
            for i in range(len(arr)):
                for j in range(len(arr)):
                    if arr[i] + arr[j] == target
        """,
        "category":   "nested_loop_search",
        "suggestion": {
            "title":  "Two-Sum Pattern: Use HashMap",
            "detail": "Classic O(n²) pair search. "
                      "A single-pass hashmap reduces this to O(n).",
            "before": "for i in range(n):\n"
                      "    for j in range(n):\n"
                      "        if arr[i]+arr[j]==target: ...",
            "after":  "seen = {}\n"
                      "for i,v in enumerate(arr):\n"
                      "    if target-v in seen: return [seen[target-v],i]\n"
                      "    seen[v] = i",
            "complexity_gain": "O(n²) → O(n)"
        }
    },
    {
        "pattern_code": """
            def fibonacci n
                return fibonacci n-1 + fibonacci n-2
            recursive calls branching exponential
        """,
        "category":   "exponential_recursion",
        "suggestion": {
            "title":  "Memoize Recursive Function",
            "detail": "Branching recursion recalculates same values. "
                      "lru_cache adds memoization in one line.",
            "before": "def fib(n):\n"
                      "    return fib(n-1)+fib(n-2)",
            "after":  "from functools import lru_cache\n"
                      "@lru_cache(maxsize=None)\n"
                      "def fib(n):\n"
                      "    return fib(n-1)+fib(n-2)",
            "complexity_gain": "O(2ⁿ) → O(n)"
        }
    },
    {
        "pattern_code": """
            result = ""
            for word in words
                result += word
            string concatenation loop append
        """,
        "category":   "string_concat_loop",
        "suggestion": {
            "title":  "Replace String += with list + join()",
            "detail": "Immutable strings make += O(n) per step. "
                      "List append is O(1), join is O(n) total.",
            "before": "s = ''\nfor w in words:\n    s += w",
            "after":  "parts = []\nfor w in words:\n    parts.append(w)\n"
                      "s = ''.join(parts)",
            "complexity_gain": "O(n²) → O(n)"
        }
    },
    {
        "pattern_code": """
            for i in range n
                for j in range n
                    for k in range n
            triple nested loop cubic
        """,
        "category":   "triple_nested",
        "suggestion": {
            "title":  "Optimize Triple Nested Loop",
            "detail": "O(n³) is very slow for large n. "
                      "Look for precomputation opportunities.",
            "before": "for i in range(n):\n"
                      "  for j in range(n):\n"
                      "    for k in range(n): ...",
            "after":  "# Precompute pairs in O(n²), then\n"
                      "# binary search for third in O(log n)\n"
                      "# Total: O(n² log n)",
            "complexity_gain": "O(n³) → O(n² log n)"
        }
    },
    {
        "pattern_code": """
            if x in my_list linear search list membership
            checking element exists array
        """,
        "category":   "linear_search",
        "suggestion": {
            "title":  "Use set() for Membership Testing",
            "detail": "'x in list' is O(n). "
                      "Converting to set makes it O(1).",
            "before": "my_list = [1,2,3,4]\nif x in my_list: ...",
            "after":  "my_set = {1,2,3,4}\nif x in my_set: ...",
            "complexity_gain": "O(n) → O(1) lookup"
        }
    },
    {
        "pattern_code": """
            sorted inside loop calling sort every iteration
            repeated sorting same list
        """,
        "category":   "sort_in_loop",
        "suggestion": {
            "title":  "Sort Once Before the Loop",
            "detail": "Sorting inside a loop is O(n² log n). "
                      "Sort once outside for O(n log n) total.",
            "before": "for item in data:\n    s = sorted(data)\n    ...",
            "after":  "s = sorted(data)\nfor item in s:\n    ...",
            "complexity_gain": "O(n² log n) → O(n log n)"
        }
    },
]


class MLSuggester:
    """
    TF-IDF based code suggestion engine.
    
    Lifecycle:
    1. __init__  → build vectorizer on knowledge base
    2. suggest() → vectorize user code, find closest match
    """

    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE

        # Extract all pattern texts for vectorizer
        pattern_texts = [
            kb["pattern_code"] for kb in self.knowledge_base
        ]

        # Build TF-IDF matrix from knowledge base
        # analyzer='word' → split on words (not chars)
        # ngram_range=(1,2) → single words AND word pairs
        # This helps match phrases like "nested loop"
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1,
            stop_words=None    # keep 'for', 'in' etc — important in code
        )

        self.kb_matrix = self.vectorizer.fit_transform(pattern_texts)

    def suggest(self, code: str,
                threshold: float = 0.08) -> list:
        """
        Find the most relevant suggestions for given code.
        
        threshold: minimum similarity score to return a suggestion
                   (0.0 = match everything, 1.0 = exact match only)
                   0.08 works well for code similarity
        """
        try:
            # Vectorize the user's code
            code_vector = self.vectorizer.transform([code])

            # Compute cosine similarity against all patterns
            similarities = cosine_similarity(
                code_vector, self.kb_matrix
            )[0]

            # Get indices sorted by similarity (highest first)
            ranked_indices = np.argsort(similarities)[::-1]

            suggestions = []
            for idx in ranked_indices:
                score = similarities[idx]

                if score < threshold:
                    break  # remaining will be even lower

                entry = self.knowledge_base[idx]
                suggestion = entry["suggestion"].copy()

                # Add ML metadata — useful for UI + debugging
                suggestion["ml_score"]    = round(float(score), 3)
                suggestion["ml_category"] = entry["category"]
                suggestion["source"]      = "ml"

                suggestions.append(suggestion)

                if len(suggestions) >= 2:  # top 2 max
                    break

            return suggestions

        except Exception as e:
            # ML should never crash the main pipeline
            print(f"ML suggester error: {e}")
            return []


# ─────────────────────────────────────────────────────────
# Singleton — build vectorizer once at startup,
# reuse for every request (expensive to rebuild)
# ─────────────────────────────────────────────────────────
_ml_suggester = None

def get_ml_suggester() -> MLSuggester:
    global _ml_suggester
    if _ml_suggester is None:
        _ml_suggester = MLSuggester()
    return _ml_suggester


def get_ml_suggestions(code: str) -> list:
    """Public API — call this from __init__.py"""
    suggester = get_ml_suggester()
    return suggester.suggest(code)