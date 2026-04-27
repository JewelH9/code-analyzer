# parser.py
# Responsibility: Convert raw code → structured data for analysis
# Approach 1: Regex-based (fast, simple, some false positives)

import re


# ─────────────────────────────────────────
# Language-specific loop patterns
# ─────────────────────────────────────────

PATTERNS = {
    "python": {
        # Matches: "for x in ..." or "for i in range(...)"
        "for_loop":    re.compile(r'^\s*for\s+\w+\s+in\s+', re.MULTILINE),

        # Matches: "while condition:"
        "while_loop":  re.compile(r'^\s*while\s+.+:', re.MULTILINE),

        # Matches: "def function_name("
        "function_def": re.compile(r'^\s*def\s+(\w+)\s*\(', re.MULTILINE),

        # Matches: lines starting with # 
        "comment":     re.compile(r'^\s*#.*$', re.MULTILINE),

        # Matches: anything inside quotes (to ignore loop keywords in strings)
        "string":      re.compile(r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\".*?\"|\'.*?\')', 
                                   re.DOTALL),
    },
    "cpp": {
        # Matches: "for (int i = 0; ...)" or "for(..."
        "for_loop":    re.compile(r'^\s*for\s*\(', re.MULTILINE),

        # Matches: "while (" or "while("
        "while_loop":  re.compile(r'^\s*while\s*\(', re.MULTILINE),

        # Matches: return type + function name + (
        "function_def": re.compile(r'\b\w+\s+(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE),

        # Matches: // comment or /* comment */
        "comment":     re.compile(r'(//.*?$|/\*.*?\*/)', re.MULTILINE | re.DOTALL),

        # Matches: strings in double quotes
        "string":      re.compile(r'".*?"', re.DOTALL),
    }
}


def remove_noise(code: str, language: str) -> str:
    """
    Remove comments and strings before analysis.
    This reduces false positives.

    Example:
        # for loop here     ← we remove this comment
        x = "for i in n"   ← we remove this string content
    """
    patterns = PATTERNS.get(language, PATTERNS["python"])

    # Replace strings with empty placeholder
    cleaned = patterns["string"].sub('""', code)

    # Remove comments
    cleaned = patterns["comment"].sub('', cleaned)

    return cleaned


def calculate_nesting_depth(code: str, language: str) -> dict:
    """
    FIXED: Track active loop stack instead of dividing indent.
    
    How it works:
    - Walk line by line
    - Maintain a stack of (indent_level) for each active loop
    - When a new loop is found:
        * Pop any stack entries with indent >= current indent
          (those loops have ended)
        * Current depth = stack size + 1
        * Push current indent onto stack
    - When a non-loop line dedents past a loop → pop that loop
    
    Example:
        def f():                    indent=0  stack=[]
            for i in range(n):      indent=4  stack=[] → push → [4]  depth=1 ✅
                for j in range(n):  indent=8  stack=[4] → push → [4,8] depth=2 ✅
            for k in range(n):      indent=4  stack=[4,8]
                                              pop 8 (≥4), pop 4 (≥4)
                                              stack=[] → push → [4]  depth=1 ✅
    """
    lines    = code.split('\n')
    patterns = PATTERNS.get(language, PATTERNS["python"])

    loop_lines     = []
    depth_map      = {}
    max_loop_depth = 0

    # ─────────────────────────────────────
    # PYTHON — indent stack approach
    # ─────────────────────────────────────
    if language == "python":
        # Stack stores indent levels of currently active loops
        loop_indent_stack = []

        for line_num, line in enumerate(lines, start=1):
            # Skip blank lines
            if not line.strip():
                continue

            current_indent = len(line) - len(line.lstrip())

            # Pop loops from stack that have ended
            # A loop ends when we see a line at same or lower indent
            while loop_indent_stack and \
                  current_indent <= loop_indent_stack[-1]:
                loop_indent_stack.pop()

            # Is this line a loop?
            is_loop = (patterns["for_loop"].match(line) or
                       patterns["while_loop"].match(line))

            if is_loop:
                # Depth = number of still-active loops + 1
                depth = len(loop_indent_stack) + 1

                loop_lines.append(line_num)
                depth_map[line_num] = depth
                max_loop_depth = max(max_loop_depth, depth)

                # Push this loop's indent onto stack
                loop_indent_stack.append(current_indent)

    # ─────────────────────────────────────
    # C++ — brace stack approach (already fixed)
    # ─────────────────────────────────────
    elif language == "cpp":
        brace_stack = []

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            current_loop_depth = brace_stack.count("loop")

            is_loop = (patterns["for_loop"].match(stripped) or
                       patterns["while_loop"].match(stripped))

            if is_loop:
                depth = current_loop_depth + 1
                loop_lines.append(line_num)
                depth_map[line_num] = depth
                max_loop_depth = max(max_loop_depth, depth)

                if '{' in line:
                    brace_stack.append("loop")
                else:
                    brace_stack.append("loop_pending")
            else:
                if '{' in line:
                    if brace_stack and \
                       brace_stack[-1] == "loop_pending":
                        brace_stack[-1] = "loop"
                    else:
                        brace_stack.append("other")

            for char in line:
                if char == '}':
                    if brace_stack:
                        brace_stack.pop()

    return {
        "max_loop_depth": max_loop_depth,
        "loop_lines":     loop_lines,
        "depth_map":      depth_map
    }


def detect_recursion(code: str, language: str) -> dict:
    """
    Detect if any function calls itself → recursion.

    Strategy:
    1. Find all function definitions → get their names
    2. For each function, check if its name appears
       inside its own body

    Returns:
    {
        "has_recursion": True/False,
        "recursive_functions": ["fibonacci", "factorial"]
    }
    """
    # These are never truly recursive in our context
    BLOCKLIST = ['main', 'Main', 'setup', 'loop']

    patterns = PATTERNS.get(language, PATTERNS["python"])
    recursive_functions = []

    # Find all function names
    function_names = patterns["function_def"].findall(code)

    for func_name in function_names:

        # ← THIS LINE WAS MISSING IN YOUR VERSION
        if func_name in BLOCKLIST:
            continue

        # Find where function starts
        if language == "python":
            func_pattern = re.compile(
                rf'def\s+{func_name}\s*\(.*?(?=\ndef\s|\Z)',
                re.DOTALL
            )
        else:
            func_pattern = re.compile(
                rf'\b\w+\s+{func_name}\s*\([^)]*\)\s*\{{.*?\}}',
                re.DOTALL
            )

        match = func_pattern.search(code)
        if match:
            func_body = match.group()
            # Check if function name appears in its own body
            # (after the definition line)
            body_after_def = func_body.split('\n', 1)[-1]
            if func_name in body_after_def:
                recursive_functions.append(func_name)

    return {
        "has_recursion": len(recursive_functions) > 0,
        "recursive_functions": recursive_functions
    }


def parse_code(code: str, language: str) -> dict:
    """
    MAIN PARSER FUNCTION
    Orchestrates all parsing steps and returns
    a complete structured picture of the code.
    """
    # Step 1: Remove noise (comments, strings)
    cleaned_code = remove_noise(code, language)

    # Step 2: Get nesting info
    nesting = calculate_nesting_depth(cleaned_code, language)

    # Step 3: Detect recursion
    recursion = detect_recursion(cleaned_code, language)

    # Step 4: Count total loops
    patterns = PATTERNS.get(language, PATTERNS["python"])
    total_for_loops  = len(patterns["for_loop"].findall(cleaned_code))
    total_while_loops = len(patterns["while_loop"].findall(cleaned_code))

    return {
        "raw_code":         code,
        "cleaned_code":     cleaned_code,
        "language":         language,
        "lines":            code.split('\n'),
        "line_count":       len(code.split('\n')),
        "total_loops":      total_for_loops + total_while_loops,
        "max_loop_depth":   nesting["max_loop_depth"],
        "loop_lines":       nesting["loop_lines"],
        "depth_map":        nesting["depth_map"],
        "has_recursion":    recursion["has_recursion"],
        "recursive_functions": recursion["recursive_functions"],
    }