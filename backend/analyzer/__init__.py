# analyzer/__init__.py (final version)

from .parser       import parse_code
from .complexity   import estimate_complexity
from .detector     import detect_issues
from .suggester    import generate_suggestions
from .ml_suggester import get_ml_suggestions


def analyze_code(code: str, language: str) -> dict:
    """
    Full pipeline:
    parse → detect → estimate → suggest (rule) → suggest (ML)
    """
    parsed     = parse_code(code, language)
    
    issues     = detect_issues(parsed)
    complexity = estimate_complexity(parsed)

    # Rule-based suggestions
    rule_suggestions = generate_suggestions(issues, parsed)

    # ML suggestions (run in parallel conceptually)
    ml_suggestions = get_ml_suggestions(code)

    # Merge: ML suggestions first (novel finds),
    # then rule-based (confirmed issues)
    # Deduplicate by title
    seen_titles  = {s["title"] for s in rule_suggestions}
    merged = list(rule_suggestions)

    for ml_s in ml_suggestions:
        if ml_s["title"] not in seen_titles:
            merged.append(ml_s)
            seen_titles.add(ml_s["title"])

    return {
        "time_complexity": complexity,
        "issues":          issues,
        "suggestions":     merged,
        "meta": {
            "language":      language,
            "line_count":    parsed["line_count"],
            "total_loops":   parsed["total_loops"],
            "has_recursion": parsed["has_recursion"],
        }
    }