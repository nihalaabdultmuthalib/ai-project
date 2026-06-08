def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> list[str]:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + max_chars, len(cleaned))
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks
