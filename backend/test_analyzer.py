# test_analyzer.py — Run this directly to test without the server

from analyzer import analyze_code

test_cases = [
    {
        "name": "Nested Loop (O(n²))",
        "language": "python",
        "code": """
def find_pairs(arr):
    result = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i] + arr[j] == 10:
                result.append((i, j))
    return result
"""
    },
    {
        "name": "Fibonacci Recursion (O(2ⁿ))",
        "language": "python",
        "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    },
    {
        "name": "Single Loop (O(n))",
        "language": "python",
        "code": """
def find_max(arr):
    max_val = arr[0]
    for item in arr:
        if item > max_val:
            max_val = item
    return max_val
"""
    },
    {
        "name": "String concat in loop",
        "language": "python",
        "code": """
def build_string(words):
    result = ""
    for word in words:
        result += word
    return result
"""
    },
    {
    "name": "C++ Sequential Loops → should be O(n)",
    "language": "cpp",
    "code": """
void sequentialTest(int n) {
    for (int i = 0; i < n; i++) {
        std::cout << i << std::endl;
    }
    for (int j = 0; j < n; j++) {
        std::cout << j << std::endl;
    }
}
"""
    },
    {
    "name": "C++ Nested Loops → should be O(n²)",
    "language": "cpp",
    "code": """
void nestedTest(int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            std::cout << i << j << std::endl;
        }
    }
}
"""
    },
]

for test in test_cases:
    print(f"\n{'='*50}")
    print(f"TEST: {test['name']}")
    print(f"{'='*50}")
    result = analyze_code(test["code"], test["language"])
    print(f"Complexity : {result['time_complexity']}")
    print(f"Issues     :")
    for issue in result["issues"]:
        print(f"  {issue}")
    print(f"Suggestions:")
    for s in result["suggestions"]:
        print(f"  {s}")