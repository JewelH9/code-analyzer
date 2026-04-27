# executor.py
# Responsibility: Safely execute code and measure runtime.
#
# Safety measures we implement:
#   1. Timeout       — kill process after N seconds
#   2. Blocklist     — reject dangerous imports/calls
#   3. No shell      — subprocess without shell=True
#   4. Capture only  — we read output, never eval() it

import subprocess
import tempfile
import os
import time
import re
import sys


# ─────────────────────────────────────────────────────────
# SAFETY: Patterns we refuse to execute
# ─────────────────────────────────────────────────────────
BLOCKED_PATTERNS = {
    "python": [
        r'\bos\s*\.\s*system\b',        # os.system()
        r'\bos\s*\.\s*popen\b',         # os.popen()
        r'\bsubprocess\b',              # subprocess module
        r'\beval\s*\(',                 # eval()
        r'\bexec\s*\(',                 # exec()
        r'\b__import__\s*\(',           # __import__()
        r'\bopen\s*\(',                 # file operations
        r'\bsocket\b',                  # network access
        r'\bshutil\b',                  # file operations
        r'\bpickle\b',                  # deserialization
        r'while\s+True\s*:(?!\s*\n\s*(if|break))',  # infinite loop
    ],
    "cpp": [
        r'\bsystem\s*\(',               # system()
        r'\bpopen\s*\(',                # popen()
        r'\bexec[lv]?\s*\(',            # exec family
        r'#\s*include\s*<fstream>',     # file I/O
        r'#\s*include\s*<cstdlib>',     # system calls
    ]
}

# Execution limits
MAX_TIMEOUT_SECONDS = 5
MAX_OUTPUT_CHARS    = 2000


def is_safe(code: str, language: str) -> tuple[bool, str]:
    """
    Check code against blocklist before executing.
    Returns (is_safe, reason_if_unsafe)
    """
    patterns = BLOCKED_PATTERNS.get(language, [])

    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            matched = re.search(pattern, code, re.IGNORECASE)
            return False, f"Blocked pattern detected: '{matched.group()}'"

    return True, ""


def execute_python(code: str) -> dict:
    """
    Execute Python code in a subprocess with timeout.
    
    Strategy:
    1. Write code to a temp file
    2. Run it with subprocess (no shell)
    3. Capture output + measure wall time
    4. Kill if timeout exceeded
    5. Clean up temp file
    """

    # Wrap user code with a timing harness
    # We inject timing AROUND their code
    harness = f"""
import time as __time
__start = __time.perf_counter()

# ── USER CODE START ──
{code}
# ── USER CODE END ──

__end = __time.perf_counter()
print(f"\\n__EXEC_TIME__{{(__end - __start) * 1000:.4f}}ms")
"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(harness)
        tmp_path = f.name

    try:
        start_wall = time.perf_counter()

        result = subprocess.run(
            [sys.executable, tmp_path],  # use same Python as server
            capture_output=True,
            text=True,
            timeout=MAX_TIMEOUT_SECONDS,
            # Security: no shell, no extra env
            shell=False,
        )

        wall_time = (time.perf_counter() - start_wall) * 1000

        # Parse output — separate user output from timing marker
        raw_output = result.stdout
        exec_time_ms = None

        if "__EXEC_TIME__" in raw_output:
            lines = raw_output.split('\n')
            user_lines = []
            for line in lines:
                if line.startswith("__EXEC_TIME__"):
                    try:
                        exec_time_ms = float(
                            line.replace("__EXEC_TIME__", "")
                                .replace("ms", "")
                                .strip()
                        )
                    except ValueError:
                        pass
                else:
                    user_lines.append(line)
            user_output = '\n'.join(user_lines).strip()
        else:
            user_output = raw_output.strip()

        # Truncate long output
        if len(user_output) > MAX_OUTPUT_CHARS:
            user_output = user_output[:MAX_OUTPUT_CHARS] + \
                          "\n... (output truncated)"

        return {
            "success":      result.returncode == 0,
            "output":       user_output,
            "error":        result.stderr.strip() if result.stderr else None,
            "exec_time_ms": exec_time_ms or wall_time,
            "timed_out":    False
        }

    except subprocess.TimeoutExpired:
        return {
            "success":      False,
            "output":       "",
            "error":        f"Execution timed out after "
                            f"{MAX_TIMEOUT_SECONDS} seconds",
            "exec_time_ms": None,
            "timed_out":    True
        }

    finally:
        # Always clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def execute_code(code: str, language: str) -> dict:
    """
    Main entry point for code execution.
    Runs safety check first, then executes.
    """
    # Step 1: Safety check
    safe, reason = is_safe(code, language)
    if not safe:
        return {
            "success":      False,
            "output":       "",
            "error":        f"⛔ Execution blocked: {reason}",
            "exec_time_ms": None,
            "timed_out":    False,
            "blocked":      True
        }

    # Step 2: Execute
    if language == "python":
        return execute_python(code)

    elif language == "cpp":
        return execute_cpp(code)

    return {
        "success": False,
        "error":   f"Execution not supported for {language} yet"
    }


def execute_cpp(code: str) -> dict:
    """
    C++ execution:
    1. Write to temp .cpp file
    2. Compile with g++
    3. Run compiled binary with timeout
    4. Clean up both files
    """
    import platform

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.cpp',
        delete=False, encoding='utf-8'
    ) as f:
        f.write(code)
        src_path = f.name

    # Binary output path
    bin_path = src_path.replace('.cpp', 
                '.exe' if platform.system() == 'Windows' else '.out')

    try:
        # Step 1: Compile
        compile_result = subprocess.run(
            ['g++', '-O0', '-o', bin_path, src_path],
            capture_output=True, text=True, timeout=15
        )

        if compile_result.returncode != 0:
            return {
                "success": False,
                "output":  "",
                "error":   f"Compilation error:\n{compile_result.stderr}",
                "exec_time_ms": None,
                "timed_out": False
            }

        # Step 2: Run
        start = time.perf_counter()
        run_result = subprocess.run(
            [bin_path],
            capture_output=True, text=True,
            timeout=MAX_TIMEOUT_SECONDS,
            shell=False
        )
        elapsed = (time.perf_counter() - start) * 1000

        output = run_result.stdout.strip()
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + "\n...(truncated)"

        return {
            "success":      run_result.returncode == 0,
            "output":       output,
            "error":        run_result.stderr.strip() or None,
            "exec_time_ms": round(elapsed, 4),
            "timed_out":    False
        }

    except subprocess.TimeoutExpired:
        return {
            "success":   False,
            "output":    "",
            "error":     f"Timed out after {MAX_TIMEOUT_SECONDS}s",
            "exec_time_ms": None,
            "timed_out": True
        }

    finally:
        for path in [src_path, bin_path]:
            if os.path.exists(path):
                os.unlink(path)