# complexity.py (fixed rule order)
# Loop depth checks FIRST, recursion checks AFTER
# Reason: nested loops are more reliably detected than recursion
# A C++ file with main() was falsely triggering recursion rule
# before we even checked for nested loops

def estimate_complexity(parsed: dict) -> dict:
    """
    Returns:
    {
        "label":      "O(n²)",
        "confidence": "high",
        "reason":     "Nested loop at depth 2 detected"
    }

    Rule order (IMPORTANT — first match wins):
    1. Triple nested loop → O(n³)   ← loops checked FIRST
    2. Double nested loop → O(n²)
    3. Branching recursion → O(2ⁿ)  ← recursion checked AFTER
    4. Linear recursion → O(n)
    5. Single loop → O(n)
    6. Nothing → O(1)
    """
    depth       = parsed.get("max_loop_depth", 0)
    has_rec     = parsed.get("has_recursion", False)
    rec_funcs   = parsed.get("recursive_functions", [])
    total_loops = parsed.get("total_loops", 0)

    # ─────────────────────────────────────────────
    # LOOP CHECKS FIRST (most reliable signal)
    # ─────────────────────────────────────────────

    if depth >= 3:
        return {
            "label":      "O(n³)",
            "confidence": "high",
            "reason":     "Triple nested loop detected"
        }

    if depth == 2:
        return {
            "label":      "O(n²)",
            "confidence": "high",
            "reason":     "Nested loop detected at depth 2"
        }

    # ─────────────────────────────────────────────
    # RECURSION CHECKS AFTER (can have false positives)
    # ─────────────────────────────────────────────

    if has_rec and _has_branching_recursion(
                        parsed["cleaned_code"], rec_funcs):
        return {
            "label":      "O(2ⁿ)",
            "confidence": "high",
            "reason":     f"Branching recursion in "
                          f"'{', '.join(rec_funcs)}'"
        }

    if has_rec:
        return {
            "label":      "O(n)",
            "confidence": "medium",
            "reason":     f"Linear recursion in "
                          f"'{', '.join(rec_funcs)}' "
                          f"(assumed single branch)"
        }

    # ─────────────────────────────────────────────
    # SINGLE LOOP
    # ─────────────────────────────────────────────

    if depth == 1 or total_loops > 0:
        return {
            "label":      "O(n)",
            "confidence": "medium",
            "reason":     "Single loop — assumes loop runs n times"
        }

    # ─────────────────────────────────────────────
    # NO LOOPS, NO RECURSION
    # ─────────────────────────────────────────────

    return {
        "label":      "O(1)",
        "confidence": "medium",
        "reason":     "No loops or recursion detected"
    }


def _has_branching_recursion(code: str,
                              recursive_functions: list) -> bool:
    import re
    for func_name in recursive_functions:
        body_pattern = re.compile(
            rf'def\s+{func_name}.*?(?=\ndef\s|\Z)', re.DOTALL
        )
        match = body_pattern.search(code)
        if match:
            body = match.group()
            call_count = len(
                re.findall(rf'\b{func_name}\s*\(', body)
            ) - 1
            if call_count > 1:
                return True
    return False