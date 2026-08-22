from src.chunk import chunk_text


def test_short_text_makes_at_least_one_chunk():
    chunks = chunk_text("Hello EvidenceQA", source="x.txt", chunk_size=50, overlap=10)
    assert len(chunks) >= 1
    assert chunks[0].source == "x.txt"
    assert "Hello" in chunks[0].text


def test_overlap_must_be_smaller_than_size():
    try:
        chunk_text("abc", source="x.txt", chunk_size=10, overlap=10)
        assert False, "expected ValueError"
    except ValueError:
        pass