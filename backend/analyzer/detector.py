# detector.py
# Responsibility: Find specific inefficient patterns
# Each detection function returns a list of issue strings.

import re


def detect_issues(parsed: dict) -> list:
    """
    Runs all detectors and collects issues.
    Returns list of human-readable issue descriptions.
    """
    issues = []

    issues += _detect_nested_loops(parsed)
    issues += _detect_redundant_computations(parsed)
    issues += _detect_string_concatenation_in_loop(parsed)
    issues += _detect_dangerous_recursion(parsed)

    if not issues:
        issues.append("✅ No major issues detected")

    return issues


def _detect_nested_loops(parsed: dict) -> list:
    issues = []
    depth_map = parsed.get("depth_map", {})

    for line_num, depth in depth_map.items():
        if depth >= 2:
            superscripts = {2: '²', 3: '³', 4: '⁴'}
            superscript = superscripts.get(depth, '²')
            issues.append(
                f"⚠️  Nested loop at line {line_num} "
                f"(depth {depth}) → likely O(n{superscript})"
            )
    return issues


def _detect_redundant_computations(parsed: dict) -> list:
    """
    Detect function calls inside loops that could be
    computed once outside.

    Example (bad):
        for i in range(n):
            result = len(arr)   ← len() called n times!

    Example (good):
        arr_len = len(arr)      ← called once
        for i in range(n):
            result = arr_len
    """
    issues = []
    lines = parsed.get("lines", [])
    language = parsed.get("language", "python")

    # Patterns that are expensive if called repeatedly
    if language == "python":
        expensive_in_loop = [
            (re.compile(r'\blen\s*\('), "len()"),
            (re.compile(r'\bsorted\s*\('), "sorted()"),
            (re.compile(r'\bsum\s*\('), "sum()"),
            (re.compile(r'\bmax\s*\('), "max()"),
            (re.compile(r'\bmin\s*\('), "min()"),
        ]
    else:
        expensive_in_loop = [
            (re.compile(r'\bstrlen\s*\('), "strlen()"),
            (re.compile(r'\bsizeof\s*\('), "sizeof()"),
        ]

    # Track if we're inside a loop
    in_loop = False
    loop_indent = 0

    for line_num, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Detect loop start
        if re.match(r'for\s+|while\s+', stripped):
            in_loop = True
            loop_indent = indent
            continue

        # Detect loop end (dedent back to loop level or less)
        if in_loop and indent <= loop_indent and stripped:
            in_loop = False

        # Check for expensive calls inside loop
        if in_loop:
            for pattern, name in expensive_in_loop:
                if pattern.search(line):
                    issues.append(
                        f"⚠️  '{name}' called inside loop at line {line_num} "
                        f"— consider moving outside the loop"
                    )
                    break  # one issue per line is enough

    return issues


def _detect_string_concatenation_in_loop(parsed: dict) -> list:
    """
    In Python, strings are IMMUTABLE.
    Doing str += "x" inside a loop creates a new string
    object each time → O(n²) memory behavior.

    Fix: Use a list and ''.join() at the end.
    """
    if parsed.get("language") != "python":
        return []

    issues = []
    lines = parsed.get("lines", [])
    in_loop = False
    loop_indent = 0
    str_concat_pattern = re.compile(r'\w+\s*\+=\s*["\']')

    for line_num, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if re.match(r'for\s+|while\s+', stripped):
            in_loop = True
            loop_indent = indent
            continue

        if in_loop and indent <= loop_indent and stripped:
            in_loop = False

        if in_loop and str_concat_pattern.search(line):
            issues.append(
                f"⚠️  String concatenation with '+=' at line {line_num} "
                f"inside a loop — use list + ''.join() instead"
            )

    return issues


def _detect_dangerous_recursion(parsed: dict) -> list:
    """
    Flag exponential recursion — it's the #1 performance killer.
    """
    issues = []

    if parsed.get("has_recursion"):
        funcs = parsed.get("recursive_functions", [])
        for func in funcs:
            issues.append(
                f"⚠️  Recursive function '{func}' detected "
                f"— verify base case exists and consider memoization"
            )

    return issues