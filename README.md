# 🧠 Knowledge Pipeline: Autonomous Research Agent

An intelligent "Second Brain" assistant that autonomously collects, synthesizes, and archives deep research from various media sources (YouTube, Web, Articles) into a local Obsidian vault.

## 🚀 The Workflow
1. **Source Collection**: Send a YouTube link or a topic to the Telegram Bot.
2. **Autonomous Research**: The agent expands the query into multiple search angles via **Tavily**.
3. **Smart Scraping**: **Jina AI** scrapes content while a **3-Layer Defense** filters out junk/404s.
4. **Dual-LLM Synthesis**: 
   - **Ollama - gemma4:e2b** (Local) handles initial mapping and extraction.
   - **Gemini 2.5 Flash** (Cloud) performs the final high-quality reduction.
5. **Obsidian Archival**: A beautifully formatted Markdown report is saved to your local vault with top-source citations.

## ✨ Key Features (Current)
- **Rolling UX**: Real-time status updates and rolling loaders in Telegram.
- **Resilient Pipeline**: Automatic snippet fallback if web scraping fails.
- **Citation Engine**: Automatically tracks and appends top 5 sources to every report.
- **Smart Memory**: SQLite-backed tracking to prevent duplicate research.

## 🛠️ Tech Stack
- **Languages**: Python (Asyncio)
- **Interface**: Telegram Bot API
- **Research**: Tavily Search & Jina AI Reader
- **LLMs**: Ollama (nomic-embed-text) & Google Gemini 2.0 Flash
- **Storage**: Obsidian (Local FS) & SQLite

## 🏗️ Project Structure
- `src/bot/`: Telegram bot handlers and UI logic.
- `src/processing/`: Researcher, Summarizer, and RAG engines.
- `src/adapters/`: External API clients (Tavily, Jina, Gemini).
- `src/storage/`: Database and Obsidian filesystem managers.

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
...
```

---
*Built for deep thinkers and knowledge workers.*
