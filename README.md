# Core

An autonomous AI agent built on LangGraph and Google Gemini, capable of browsing the web, managing files, executing searches, and maintaining persistent memory across sessions. Core accepts natural language commands and orchestrates a suite of tools to complete multi-step tasks end-to-end.

---

## Overview

Core is a general-purpose agentic system designed around a reasoning loop that plans, selects tools, executes actions, and reflects on results. The agent maintains conversational state across turns using SQLite-backed checkpointing and supports long-term knowledge retention through a ChromaDB vector store. A Playwright-controlled Chromium instance gives the agent full browser capabilities, enabling it to interact with live web pages as part of task execution.

---

## Repository Structure

```
Core/
├── main.py             Entry point and interactive command loop
├── diagnose.py         Environment and dependency diagnostic utility
├── practice.py         Sandbox for testing agent components
├── test_memory.py      Memory system unit tests
├── requirements.txt    Project dependencies
├── browser_state.db    SQLite checkpoint store for session persistence
├── state.db            Supplementary state database
├── core_db/            ChromaDB vector store for long-term memory
└── src/
    ├── brain.py        LangGraph agent graph definition
    ├── tools.py        Tool definitions (search, browser, file I/O, etc.)
    └── memory.py       Vector memory read/write interface
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/AhmedTheMagnificent/Core.git
cd Core
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browser binaries:

```bash
playwright install
```

Configure environment variables by creating a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## Usage

Launch the agent:

```bash
python main.py
```

Once running, interact with the agent via the command prompt:

```
ONLINE
Session ID: <uuid>

Command > Search for the latest news on LangGraph and summarize it
... Working ...

AGENT: Here is a summary of the latest LangGraph updates...
```

Type `exit` or `quit` to terminate the session. Each session is assigned a unique ID and its state is persisted to `browser_state.db`, allowing the agent to resume context in future runs if needed.

To verify your environment before running:

```bash
python diagnose.py
```

---

## Architecture

### Reasoning Engine

The agent is orchestrated by LangGraph, which manages a stateful directed graph of reasoning steps. At each node, the agent either calls a tool or produces a final response, looping until the task is complete.

### Language Model

Google Gemini is used as the underlying language model via the `langchain-google-genai` integration. The model drives tool selection, planning, and response generation.

### Tool Layer

The agent has access to a set of tools that allow it to interact with the outside world, including web search via Tavily, browser automation via Playwright, file reading and writing via pandas and openpyxl, and HTML parsing via lxml. Screenshots are captured using Pillow for visual context when needed.

### Memory

Two forms of memory are maintained. Short-term session memory is handled by LangGraph's SQLite checkpointer, which persists the full message history across turns within a session. Long-term memory is stored in a ChromaDB vector database, allowing relevant knowledge from past interactions to be retrieved and injected into future contexts.

### Browser Control

A persistent Chromium browser instance is launched at startup via Playwright. The agent can navigate pages, click elements, fill forms, and extract content as part of multi-step workflows.

---

## Dependencies

| Category | Libraries |
|---|---|
| Orchestration | `langchain`, `langgraph`, `langchain-google-genai` |
| Memory | `chromadb`, `langchain-chroma` |
| Browser | `playwright` |
| Search | `tavily-python` |
| File Handling | `pandas`, `openpyxl`, `lxml`, `pillow` |
| Utilities | `python-dotenv`, `rich`, `pydantic` |
| Automation | `apache-airflow==2.10.3` |

---

## Future Work

Potential directions for extension include:

- A web-based or desktop UI to replace the terminal interface
- Scheduled and event-driven task execution via Airflow
- Support for additional language model providers
- Expanded tool set covering email, calendar, and API integrations
- Multi-agent coordination for parallel task execution

