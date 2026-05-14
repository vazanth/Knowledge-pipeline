JINA_BASE = "https://r.jina.ai/"

MIN_CONTENT_LENGTH = 500
JUNK_SIGNALS = [
    "404",
    "page not found",
    "not found",
    "no longer available",
    "has been removed",
    "moved permanently",
    "access denied",
    "403 forbidden",
    "enable javascript",
    "you are being redirected",
]

BLOCKED_DOMAINS = [
    "reddit.com",
    "linkedin.com",
    "quora.com",
    "pinterest.com",
    "facebook.com",
    "twitter.com",
    "x.com",
]

CREATE_SOURCE_TABLE = """CREATE TABLE IF NOT EXISTS source_platform(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    platform_type TEXT,
    platform_id TEXT UNIQUE,
    created_at TEXT
)"""

CREATE_CONTENT_TABLE = """CREATE TABLE IF NOT EXISTS source_content(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    platform_content_id TEXT UNIQUE,
    title TEXT,
    content TEXT,
    content_url TEXT,
    content_hash TEXT UNIQUE,
    fetched_at TEXT,
    FOREIGN KEY(source_id) REFERENCES source_platform(id)
)"""

CREATE_SUMMARY_TABLE = """CREATE TABLE IF NOT EXISTS content_summary(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER,
    summary TEXT,
    strategy_used TEXT,
    created_at TEXT,
    FOREIGN KEY(content_id) REFERENCES source_content(id)
)"""

INSERT_SOURCE = """
    INSERT OR IGNORE INTO source_platform (name, platform_type, platform_id, created_at) VALUES (?, ?, ?, ?)
"""

INSERT_CONTENT = """
    INSERT OR IGNORE INTO source_content(source_id, platform_content_id, title, content, content_url, content_hash, fetched_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

INSERT_SUMMARY = """
    INSERT OR IGNORE INTO content_summary(content_id, summary, strategy_used, created_at)
    VALUES (?, ?, ?, ?)
"""

SELECT_ALL_SOURCES = "select * from source_platform"

SELECT_SOURCE_NAMES = "select name from source_platform"

SELECT_LAST_FETCH_TIME = (
    "select MAX(fetched_at) from source_content where source_id = ?"
)

SELECT_CONTENT_SUMMARY = "select summary from content_summary where content_id = ?"

SELECT_CONTENT_BY_ID = "select title, content_url from source_content where id = ?"

UPDATE_SOURCE = """
    UPDATE source_platform
    SET name = ?, platform_type = ?, platform_id = ?, created_at = ?
    WHERE id = ?
"""

UPDATE_CONTENT = """
    UPDATE source_content
    SET source_id = ?, platform_content_id = ?, title = ?, content = ?, content_url = ?, content_hash = ?, fetched_at = ?
    WHERE id = ?
"""

UPDATE_SUMMARY = """
    UPDATE content_summary
    SET content_id = ?, summary = ?, created_at = ?
    WHERE id = ?
"""


WELCOME_MESSAGE = """🤖 Hey! I'm your Knowledge Bot 📚
    I help you stay updated with your favorite content without the noise.
    ✨ What you can do:
    ➕ /add_source – Add a YouTube channel or blog
    📌 /sources – View your saved sources
    🆕 /latest – Get the newest updates instantly
    Just add your favorite sources and I'll handle the rest 🚀"""

ADD_SOURCE_ERROR = "❌ Oops! Use it like this:\n/add_source <platform_id> <name>"

QUERY_ERROR = "❌ Oops! Use it like this:\n/QUERY <your question>"

ADD_SOURCE_SUCCESS = "✅ Added *{name}* to your sources 🎉\nI'll keep you updated with the latest from this source!"

UPDATES_CHECKING = "🔎 Checking your sources..."

SOURCES_EMPTY = "You haven’t added any sources yet 📭\nTry /add_source to get started!"

SOURCES_LIST = "📚 *Your Sources:*\n• {names_str}"

UPDATES_LOADING = "🔎 Gathering fresh updates for you... ⏳"

UPDATES_EMPTY = "📭 No new content right now.\nCheck back later or add more sources!"

UPDATE_FOUND = "📡 Found {count} new item(s)! Processing... ⚡"

ALL_CAUGHT_UP = "✅ All caught up! You're up to date 🎉"

GENERIC_ERROR = "❌ Oops! Something went wrong"

CREATE_DIRECT_PROMPT = """ 
You are summarizing a software engineering blog post or video transcript.

Write a final 2-3 line summary that captures:
- The exact topic and technology covered
- The specific aspects or depth covered (e.g. internals, implementation, comparison)
- Any key technical terms, components, or trade-offs mentioned

Rules:
- Be specific and dense — every word should carry information
- Preserve technical terminology exactly
- Do NOT start with "This video/article explains..."
- Do NOT be vague — bad: "covers how RAG works", good: "covers RAG retrieval pipeline using FAISS, chunking strategies, and reranking with cross-encoders"

TEXT:
{text}
"""

CREATE_MAP_PROMPT = """
You are summarizing a software engineering blog post or video transcript.

Write a final 2-3 line summary that captures:
- The exact topic and technology covered
- The specific aspects or depth covered (e.g. internals, implementation, comparison)
- Any key technical terms, components, or trade-offs mentioned

Rules:
- Be specific and dense — every word should carry information
- Preserve technical terminology exactly
- Do NOT start with "This video/article explains..."
- Do NOT be vague — bad: "covers how RAG works", good: "covers RAG retrieval pipeline using FAISS, chunking strategies, and reranking with cross-encoders"

TEXT:
{text}
"""

CREATE_REDUCE_PROMPT = """
You are combining partial summaries of a software engineering blog post or video.

Write a final 2-3 line summary that captures:
- The exact topic and technology covered
- The specific aspects or depth covered (e.g. internals, implementation, comparison)
- Any key technical terms, components, or trade-offs mentioned

Rules:
- Be specific and dense — every word should carry information
- Preserve technical terminology exactly
- Do NOT start with "This video/article explains..." 
- Do NOT be vague — bad example: "covers how RAG works", good example: "covers RAG retrieval pipeline using FAISS, chunking strategies, and reranking with cross-encoders"

SUMMARIES:
{combined}
"""

EXPAND_QUERY_PROMPT = """
You are a search query expert for software engineering research.

Given a summary, generate 5 search queries for deep technical research.
Each query must follow a DIFFERENT angle in this exact order:
1. Internal architecture / how it works under the hood  [deep]
2. Trade-offs, limitations, and failure modes  [deep]
3. Implementation patterns / production best practices  [deep]
4. Comparison with alternatives  [medium - approachable but technical]
5. Beginner-friendly breakdown of the core concept  [simple - foundation focused]

Rules:
- Each query should be 5-10 words, specific and targeted
- Return ONLY a JSON array of 5 strings, nothing else

Summary:
{summary}

Output format:
["query one", "query two", "query three", "query four", "query five"]
"""

CREATE_LIST_REDUCE_PROMPT = """
You are synthesizing research from multiple software engineering articles into a single high-signal markdown document.

OUTPUT FORMAT:
- Valid Markdown only
- Use `##` for sections, `###` only if necessary
- Use `-` for bullet points (preferred over paragraphs)
- Do NOT use **bold** as a label prefix on bullets (e.g., "**Term:** explanation" is not allowed)
- Bold is only for a term that appears inline within a sentence when first introduced
- Use `inline code` only for exact technical terms (APIs, configs, functions, protocols)
- Use code blocks with language tags only when implementation detail is present

STRUCTURE:

## Overview
- 2–3 lines maximum
- Core idea + problem + why it matters

## How It Works
- Step-by-step system or architectural explanation
- Focus on mechanisms, data flow, and components

## Implementation & Best Practices
- Concrete engineering practices only
- Include edge cases, scaling concerns, and failure handling

## Trade-offs & Limitations
- Explicit constraints, bottlenecks, and failure modes
- Include conflicting viewpoints if present:
  - Format as:
    - **Perspective A:** ...
    - **Perspective B:** ...

## Comparison with Alternatives
- Direct, technical comparisons only
- Highlight differences in complexity, performance, or use case

## Real-World Usage
- Actual systems, companies, or production patterns only

RULES:
- Each bullet must contain:
  - a specific mechanism, constraint, or design decision
  - OR a concrete example
- Merge duplicate ideas across sources — do NOT restate the same concept
- Preserve exact technical terminology
- Do not generalize beyond source material
- Omit any section with no meaningful content
- No intro or conclusion outside sections
- No filler phrases or meta commentary
- REJECT any content that is clearly about a different topic than the majority of sources
- In Real-World Usage, only include entries that name a specific company, system, or open-source project
- If a source discusses an unrelated technology, exclude it entirely from the synthesis

ARTICLE SUMMARIES:
{combined}
"""

RAG_PROMPT = """
You are a technical research assistant with access to the user's personal knowledge vault.
The vault contains research notes on software engineering topics — AI, system design, databases, DevOps, and frontend.

CONTEXT:
{context}

QUESTION:
{query}

ANSWERING RULES:
- Answer primarily from the provided context
- If the context fully covers the question, answer directly — no disclaimer needed
- If the context partially covers the question, answer what you can from the vault first, then clearly separate and answer the rest from general knowledge
- If the context has no relevant information at all, answer from general knowledge

FORMAT FOR PARTIAL OR NO VAULT COVERAGE:
⚠️ *Your vault doesn't cover [specific missing topic] yet.*

[Answer from general knowledge here]

💡 To fill this gap, use /latest to find new research or find a video and use the Explore button to add it to your knowledge base.

FORMAT RULES:
- Be concise and technical — no preamble like "Based on your notes..."
- Use bullet points for multi-part answers
- Use `inline code` for technical terms, APIs, configs, and commands
- If quoting directly from a note use > blockquote format
- When answering from vault, cite the source at the end as: Source: Note Title
- When answering from general knowledge, do not cite a source

STRICT RULES:
- Never mix vault content and general knowledge without clearly separating them
- Never present general knowledge as if it came from the vault
- Never speculate — if genuinely uncertain even from general knowledge, say so
- Any technical terms, variable names, or file names containing underscores (_) MUST be wrapped in `backticks`.
"""
