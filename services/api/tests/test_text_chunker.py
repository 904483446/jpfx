import pytest
from app.services.text_chunker import chunk_text


def test_chunk_text_uses_continuous_indexes_and_fixed_windows():
    chunks = chunk_text("abcdefghij", chunk_size=4, overlap=1)

    assert [(chunk.index, chunk.content) for chunk in chunks] == [
        (0, "abcd"),
        (1, "defg"),
        (2, "ghij"),
        (3, "j"),
    ]


def test_chunk_text_keeps_all_source_text_when_windows_overlap():
    source = "abcdefghij"
    chunks = chunk_text(source, chunk_size=4, overlap=1)

    assert (
        chunks[0].content + "".join(chunk.content[1:] for chunk in chunks[1:]) == source
    )


@pytest.mark.parametrize("chunk_size, overlap", [(0, 0), (4, -1), (4, 4)])
def test_chunk_text_rejects_invalid_window(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=chunk_size, overlap=overlap)
