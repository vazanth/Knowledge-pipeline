from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    size: int
    overlap: int
    separators: list[str]


_encoder = tiktoken.get_encoding("cl100k_base")

CHUNK_CONFIGS = {
    "transcript": ChunkConfig(
        size=700, overlap=100, separators=["\n\n", "\n", ".", "?", "!"]
    ),
    "markdown": ChunkConfig(
        size=1200, overlap=50, separators=["\n## ", "\n### ", "\n\n", "\n"]
    ),
    "scraped": ChunkConfig(size=1000, overlap=80, separators=["\n\n", "\n", ".", "?"]),
}


def token_len(text):
    return len(_encoder.encode(text))


def get_chunks(transcript, doc_type: str):
    config = CHUNK_CONFIGS.get(doc_type)

    if config is None:
        raise ValueError(f"Invalid doc_type: {doc_type}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.size,
        chunk_overlap=config.overlap,
        length_function=token_len,
        separators=config.separators,
    )

    return splitter.split_text(transcript)
