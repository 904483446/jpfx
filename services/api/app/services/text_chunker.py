from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str


def chunk_text(
    text: str, *, chunk_size: int = 1000, overlap: int = 150
) -> list[TextChunk]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size 必须大于 overlap，且 overlap 不能小于 0")

    step = chunk_size - overlap
    return [
        TextChunk(index=index, content=text[start : start + chunk_size])
        for index, start in enumerate(range(0, len(text), step))
    ]
