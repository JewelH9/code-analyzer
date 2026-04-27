# ⚡ Real-Time Code Performance Analyzer

A full-stack web application that analyzes Python and C++ code for time complexity, detects inefficient patterns, and suggests optimizations — powered by a rule-based engine and a TF-IDF ML layer.

🔗 **Live Demo:** [code-analyzer-lac.vercel.app](https://code-analyzer-lac.vercel.app)  
🔗 **Backend API:** [code-analyzer-backend-yvrg.onrender.com](https://code-analyzer-backend-yvrg.onrender.com/health)

---

## 📸 Preview

![Code Analyzer Preview](https://code-analyzer-lac.vercel.app/preview.png)

---

## 🚀 Features

- **Time Complexity Estimation** — Detects O(1), O(n), O(n²), O(n³), O(2ⁿ) with confidence level and reason
- **Pattern Detection** — Flags nested loops, string concatenation in loops, expensive calls inside loops, dangerous recursion
- **Optimization Suggestions** — Before/after code examples with complexity gain (e.g. O(n²) → O(n))
- **ML-Powered Suggestions** — TF-IDF cosine similarity engine surfaces additional suggestions beyond rule-based detection
- **Code Execution** — Sandboxed execution with real runtime measurement in milliseconds
- **Multi-Language** — Supports Python and C++
- **One-Click Examples** — Pre-loaded test cases for quick exploration

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Tailwind CSS |
| Backend | Python, Flask, Flask-CORS |
| ML Engine | Scikit-learn (TF-IDF + Cosine Similarity) |
| Parsing | Regex-based + AST-inspired indent/brace stack |
| Execution | Python subprocess with sandboxing |
| Deployment | Vercel (frontend), Render (backend) |

---

## 🧠 How It Works

```
User pastes code
      │
      ▼
React Frontend
      │  POST /analyze
      ▼
Flask Backend
      │
      ▼
┌─────────────────────────────────────┐
│         ANALYZER ENGINE             │
│                                     │
│  1. Parser     → extracts structure │
│  2. Detector   → finds issues       │
│  3. Complexity → assigns Big-O      │
│  4. Suggester  → generates fixes    │
│  5. ML Engine  → TF-IDF similarity  │
└─────────────────────────────────────┘
      │
      ▼
JSON Response
{ time_complexity, issues, suggestions }
      │
      ▼
React renders results
```

### Complexity Rules (in order of priority)
| Pattern | Complexity |
|---------|-----------|
| Triple nested loop | O(n³) |
| Double nested loop | O(n²) |
| Branching recursion (e.g. Fibonacci) | O(2ⁿ) |
| Linear recursion (e.g. factorial) | O(n) |
| Single loop | O(n) |
| No loops or recursion | O(1) |

---

## 📁 Project Structure

```
code-analyzer/
│
├── backend/                        # Flask API
│   ├── app.py                      # Entry point, routes
│   ├── requirements.txt
│   ├── Procfile                    # Render deployment
│   ├── runtime.txt
│   └── analyzer/
│       ├── __init__.py             # Pipeline orchestrator
│       ├── parser.py               # Code structure extraction
│       ├── complexity.py           # Big-O estimator
│       ├── detector.py             # Issue detection
│       ├── suggester.py            # Rule-based suggestions
│       └── ml_suggester.py         # TF-IDF ML suggestions
│
└── frontend/                       # React app
    └── src/
        ├── App.jsx                 # Root, state management
        ├── api/
        │   └── analyze.js          # API layer
        └── components/
            ├── Header.jsx
            ├── CodeEditor.jsx
            ├── ResultPanel.jsx
            ├── ComplexityBadge.jsx
            ├── IssuesList.jsx
            ├── SuggestionsList.jsx
            └── ExecutionPanel.jsx
```

---

## 🔌 API Reference

### `GET /health`
Returns server status.

```json
{ "status": "ok" }
```

### `POST /analyze`
Analyzes code for complexity and issues.

**Request:**
```json
{
  "code": "for i in range(n):\n    for j in range(n):\n        pass",
  "language": "python"
}
```

**Response:**
```json
{
  "time_complexity": {
    "label": "O(n²)",
    "confidence": "high",
    "reason": "Nested loop detected at depth 2"
  },
  "issues": [
    "⚠️  Nested loop at line 1 (depth 2) → likely O(n²)"
  ],
  "suggestions": [
    {
      "title": "Replace Nested Loop with HashMap",
      "detail": "A nested loop checking pairs costs O(n²)...",
      "before": "for i in range(n):\n    for j in range(n): ...",
      "after": "seen = {}\nfor i, val in enumerate(arr): ...",
      "complexity_gain": "O(n²) → O(n)"
    }
  ],
  "meta": {
    "language": "python",
    "line_count": 3,
    "total_loops": 2,
    "has_recursion": false
  }
}
```

### `POST /execute`
Executes code in a sandboxed subprocess.

**Request:**
```json
{
  "code": "print('hello world')",
  "language": "python"
}
```

**Response:**
```json
{
  "success": true,
  "output": "hello world",
  "error": null,
  "exec_time_ms": 0.034,
  "timed_out": false
}
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- g++ (for C++ execution)

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm start
# Runs on http://localhost:3000
```

### Environment Variables

Create `frontend/.env.local`:
```
REACT_APP_API_URL=http://localhost:5000
```

---

## 🔒 Security

The execution sandbox implements:
- **Blocklist** — rejects `os.system`, `subprocess`, `eval`, `exec`, file I/O, and network calls
- **Timeout** — kills process after 5 seconds (prevents infinite loops)
- **No shell** — subprocess runs with `shell=False`
- **Output cap** — truncates output at 2000 characters

> ⚠️ This is a development-grade sandbox. Production use would require Docker with `--network none` and memory/CPU limits.

---

## 🧪 Test Cases

| Code Pattern | Expected Complexity |
|-------------|-------------------|
| Single for loop | O(n) |
| Nested for loops | O(n²) |
| Triple nested loops | O(n³) |
| Fibonacci recursion | O(2ⁿ) |
| Factorial recursion | O(n) |
| No loops | O(1) |
| C++ sequential loops | O(n) — not O(n²) |
| C++ matrix multiply | O(n³) |

---

## 🔮 Future Improvements

- **AST parsing** — replace regex with Python `ast` module for zero false positives
- **Docker sandbox** — true isolation with network/memory/CPU limits
- **More languages** — Java, JavaScript, Go support
- **O(n log n) detection** — detect binary search inside loops
- **Space complexity** — analyze memory usage patterns
- **Larger ML knowledge base** — more training patterns for better suggestions
- **User accounts** — save and compare analysis history

---

## 🎓 Key Design Decisions

**Why Flask over Django?**
Flask is lightweight and minimal — perfect for a focused REST API. Django's full framework features (ORM, admin, auth) would be overkill for two endpoints.

**Why TF-IDF over an LLM?**
No API cost, no latency, fully offline, and explainable. TF-IDF cosine similarity runs in milliseconds and shows exactly why it matched a pattern.

**Why separate modules (Parser, Detector, Complexity, Suggester)?**
Single Responsibility Principle — each module does one job. Swapping the regex parser for an AST parser requires changing only `parser.py`, nothing else.

**Why rule-based before ML?**
Rule-based gives deterministic, explainable results for known patterns. ML adds value for fuzzy matches and patterns the rules don't cover. Layering them gives the best of both.

---

## 👨‍💻 Author

**JewelH9**  
Final Year CS Student  
[GitHub](https://github.com/JewelH9/code-analyzer)

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
