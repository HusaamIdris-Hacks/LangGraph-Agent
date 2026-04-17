# LangGraph Agent

Personal learning repo for building agents with **LangGraph**, **LangChain**, and **Google Gemini**. Examples progress from a simple tool-calling agent to a small reflection loop implemented as a state graph.

## Contents

| Path | Description |
|------|-------------|
| `1_Introduction/react_agent_basic.py` | Minimal agent using LangChain’s `create_agent` with Gemini and Tavily search. |
| `2_basic_reflection_system/` | **Generate → reflect → generate** loop built with `StateGraph`, conditional edges, and message state. |

## Prerequisites

- Python 3.11+ (matches the project’s `venv`)
- A [Google AI Studio](https://aistudio.google.com/) API key (Gemini)
- A [Tavily](https://www.tavily.com/) API key (for the intro agent’s search tool)

## Setup

1. **Clone the repo** (do not commit secrets; `.env` is gitignored).

2. **Create and activate a virtual environment** (recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
