# 🧠 Knowledge Pipeline: Autonomous Research Agent

An intelligent "Second Brain" assistant that autonomously collects, synthesizes, and archives deep research from various media sources into a local Obsidian vault — then lets you **query your own knowledge** using RAG-powered semantic search.

## 🚀 The Workflow

### Phase 1 — Collect & Synthesize
1. **Source Collection**: Add YouTube channels via `/add_source` and fetch latest videos with `/latest`.
2. **Autonomous Research**: The agent expands summaries into multiple search angles via **Tavily**.
3. **Smart Scraping**: **Jina AI** scrapes content while a **3-Layer Defense** filters out junk/404s.
4. **Dual-LLM Synthesis**: 
   - **Ollama - gemma3:4b** (Local) handles initial mapping and extraction.
   - **Gemini 2.5 Flash** (Cloud) performs the final high-quality reduction.
5. **Obsidian Archival**: A beautifully formatted Markdown report is saved to your local vault with top-source citations.

### Phase 2 — Index & Query
6. **Auto-Indexing**: On startup, the bot scans your entire Obsidian vault, chunks each note, and embeds them into **ChromaDB**.
7. **Semantic Search**: Use `/query` to ask natural language questions against your vault.
8. **Distance Filtering**: Only truly relevant results (distance < 1.3) are used — irrelevant matches are filtered out.
9. **Grounded Answers**: Gemini generates answers strictly from your vault data, with hallucination-free source citations stapled to every response.

## ✨ Key Features
- **Rolling UX**: Real-time status updates and rolling loaders in Telegram.
- **Resilient Pipeline**: Automatic snippet fallback if web scraping fails.
- **Citation Engine**: Automatically tracks and appends verified source URLs to every response.
- **Smart Memory**: SQLite-backed tracking to prevent duplicate research.
- **RAG Search**: Ask questions in natural language and get answers grounded in your own research.
- **Distance-Based Filtering**: Prevents false positives — the bot honestly tells you when your vault doesn't cover a topic.
- **Metadata Preservation**: Obsidian frontmatter (title, tags, source, date) is stored alongside embeddings for rich attribution.

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| **Language** | Python 3.x (Asyncio) |
| **Interface** | Telegram Bot API |
| **Research** | Tavily Search & Jina AI Reader |
| **LLMs** | Ollama (gemma3:4b) & Google Gemini 2.5 Flash |
| **Embeddings** | Ollama (nomic-embed-text) |
| **Vector Store** | ChromaDB (Persistent, Local) |
| **Database** | SQLite (aiosqlite) |
| **Knowledge Base** | Obsidian (Local Filesystem) |

## 🤖 Bot Commands
| Command | Description |
|---|---|
| `/start` | Welcome message and bot introduction. |
| `/add_source <id> <name>` | Add a YouTube channel to monitor. |
| `/sources` | List all tracked sources. |
| `/latest` | Fetch, summarize, and archive new videos from all sources. |
| `/query <question>` | Ask a question against your Obsidian vault using RAG. |

## 🏗️ Project Structure
```
src/
├── bot/
│   ├── knowledge_bot.py      # App wiring, lifecycle hooks, handler registration
│   ├── handlers.py            # All command & callback logic (start, latest, query, etc.)
│   └── ui_helpers.py          # Pure UI utilities (loaders, keyboards, cast helpers)
├── processing/
│   ├── summarizer.py          # Dual-LLM Map-Reduce summarization pipeline
│   ├── researcher.py          # Tavily search + Jina web scraping orchestrator
│   ├── indexing_engine.py     # Vault scanner, chunker, and embedding upserter
│   ├── rag_engine.py          # Query embedding, vector search, and LLM synthesis
│   ├── embedding_engine.py    # Embedding model abstraction (Nomic via Ollama)
│   └── chunk.py               # Text chunking strategies (Markdown-aware)
├── adapters/
│   ├── llm/                   # Gemini & Ollama LLM clients
│   └── sources/               # YouTube transcript adapter
├── storage/
│   ├── database.py            # SQLite async database (sources, content, summaries)
│   ├── vector_store.py        # ChromaDB wrapper (upsert, retrieve with metadata)
│   ├── obsidian.py            # Obsidian vault file manager (frontmatter + MD)
│   └── models.py              # Data models
├── core/
│   ├── factory.py             # Dependency injection & app assembly
│   └── container.py           # AppContainer (holds all service instances)
├── settings/
│   ├── settings.py            # Settings dataclass
│   └── load_settings.py       # Environment loader (.env → Settings)
├── utils/
│   └── constants.py           # All prompts, messages, and string templates
└── main.py                    # Entry point (startup indexing + bot launch)
```

## 📊 Example Research Output
Every research task generates a structured Markdown file with frontmatter, categorical analysis, and verified sources:

```markdown
---
title: "The Real Reason SpaceX is Buying Cursor"
source: https://www.youtube.com/watch?v=vwme_LkfMgE
created: 2026-04-27
tags: [research, knowledge-pipeline]
---

## Overview
This document details systems for efficient code indexing, RAG for LLMs, and safe alignment...

## How It Works
- Codebases are indexed using **Merkle trees** for efficient synchronization.
- A RAG pipeline uses code embeddings stored in a vector database (e.g., Turbopuffer).

## Sources: 
- https://read.engineerscodex.com/p/how-cursor-indexes-codebases-fast
- https://medium.com/coinmonks/merkle-tree-a-simple-explanation-and-implementation-48903442bc08
```

---
*Built for deep thinkers and knowledge workers.*
