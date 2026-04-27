from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

_encoder = tiktoken.get_encoding("cl100k_base")


def token_len(text):
    return len(_encoder.encode(text))


def get_chunks(transcript):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=10,
        length_function=token_len,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""],
    )

    return splitter.split_text(transcript)
