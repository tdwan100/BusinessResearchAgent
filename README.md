# AI Business Workflow Analyst

A polished Streamlit demo app that uses a 4-agent CrewAI workflow to analyze a company website and produce a business-ready AI opportunity report.

## Features

- Streamlit UI with clean input form and professional report rendering.
- Four specialized CrewAI agents:
  1. Research Agent
  2. Offering & Market Agent
  3. Pain Point / Opportunity Agent
  4. Report Synthesizer Agent
- Structured outputs passed between stages using Pydantic schemas.
- Minimal toolset (website fetcher, page selector, text cleaner, optional enrichment note).
- Step-by-step visible progress updates.
- Markdown export of final report.
- Safe fallback report path if model runtime is unavailable.

## Project Structure

```text
.
├── agents/
├── crews/
├── schemas/
├── services/
├── tools/
├── utils/
├── app.py
└── requirements.txt
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

> Note: CrewAI will require an accessible LLM provider configuration in your environment.
