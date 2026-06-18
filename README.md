# Job Application Agent

An AI-powered job application agent built with LangGraph and FastAPI. Paste a job description and get back a fit score, skill match analysis, and a tailored cover letter — all generated automatically based on your resume.

## How It Works

The agent runs a 3-node LangGraph pipeline:

1. **Analyze JD** — extracts required skills, responsibilities, and experience level from the job description
2. **Match Skills** — compares your resume against the requirements and identifies strong matches, gaps, and a fit score out of 10
3. **Generate Output** — writes a concise, tailored cover letter based on the match analysis

## Tech Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful agent graph
- [LangChain](https://github.com/langchain-ai/langchain) — LLM orchestration
- [FastAPI](https://fastapi.tiangolo.com/) — REST API server
- [Groq](https://console.groq.com/) — free LLM inference (Llama 3.3 70B)
- Python 3.10+

## Project Structure

```
job-agent/
├── agent.py            # LangGraph pipeline (3 nodes)
├── main.py             # FastAPI server
├── resume_context.py   # Resume data and summary function
├── .env                # API keys (never commit this)
├── .gitignore
└── README.md
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/job-agent.git
cd job-agent
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install langgraph langchain langchain-anthropic langchain-groq fastapi uvicorn python-dotenv
```

**4. Set up your API key**

Create a `.env` file in the root:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

**5. Update `resume_context.py`**

Replace the resume data in `resume_context.py` with your own skills, experience, and projects.

**6. Run the server**
```bash
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to access the Swagger UI.

## Usage

Send a POST request to `/analyze` with a job description:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "We are looking for a Python backend engineer with FastAPI and AWS experience..."}'
```

**Response:**
```json
{
  "fit_score": "8/10 — Strong match with direct Python, FastAPI, and AWS experience.",
  "skill_match": "Strong Matches: Python, FastAPI, AWS, Docker...\nGaps: ...",
  "cover_letter": "Dear Hiring Manager, ..."
}
```

## Customization

- **Swap the LLM** — change the model in `agent.py` to use Anthropic Claude, OpenAI, or any LangChain-supported provider
- **Add memory** — store past analyses in Redis or a JSON file to track job fit over time
- **Add a frontend** — build a React UI to replace the Swagger interface
- **RAG over projects** — embed project descriptions into Chroma/FAISS for smarter project selection per job

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM inference |
| `ANTHROPIC_API_KEY` | (Optional) Anthropic API key if using Claude |

## License

MIT