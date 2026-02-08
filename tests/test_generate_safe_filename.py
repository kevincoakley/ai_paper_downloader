from ai_paper_downloader import generate_safe_filename


def test_slugify_title_removes_special_chars_and_normalizes_spaces():
    assert (
        generate_safe_filename.slugify_title("Hello, World! AI 2024")
        == "hello_world_ai_2024"
    )


def test_deterministic_hash_is_stable():
    assert (
        generate_safe_filename.generate_deterministic_hash("ICLR", "2024", "My Title")
        == "09d43602"
    )


def test_generate_safe_filename_format_and_max_length():
    title = "x" * 400
    filename = generate_safe_filename.generate_safe_filename("ICLR", "2024", title)
    expected_hash = generate_safe_filename.generate_deterministic_hash(
        "ICLR", "2024", title
    )

    assert filename.endswith(f"__{expected_hash}.pdf")
    assert len(filename) == 255
