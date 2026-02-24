import csv
from types import SimpleNamespace

import pytest

from ai_paper_downloader import main_entry


class _FakeParser:
    def __init__(self, papers):
        self._papers = papers

    def parse(self):
        return self._papers


class _FakeResponse:
    def __init__(self, chunks):
        self._chunks = chunks

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        del chunk_size
        for chunk in self._chunks:
            yield chunk


def test_main_downloads_pdfs_and_writes_csv(monkeypatch, tmp_path, capsys):
    papers = [
        {
            "title": "Paper One",
            "authors": "Alice",
            "category": "C1",
            "pdf_url": "https://example.com/1.pdf",
        },
        {
            "title": "Paper Two",
            "authors": "Bob",
            "category": "C2",
            "pdf_url": "https://example.com/2.pdf",
        },
    ]
    args = SimpleNamespace(
        conference="ICML",
        year="2024",
        save_dir=str(tmp_path),
        num_papers_to_download="-1",
        no_download_pdf=True,
        seconds_between_downloads="0",
    )

    monkeypatch.setattr(main_entry.command_args, "args", lambda _: args)
    monkeypatch.setattr(main_entry, "ICMLParser", lambda *_: _FakeParser(papers))
    monkeypatch.setattr(
        main_entry.generate_safe_filename,
        "generate_safe_filename",
        lambda _c, _y, title: f"{title.replace(' ', '_')}.pdf",
    )

    get_calls = []

    def fake_get(url, headers, stream):
        get_calls.append((url, headers, stream))
        return _FakeResponse([f"content:{url}".encode("utf-8")])

    sleep_calls = []

    monkeypatch.setattr(main_entry.requests, "get", fake_get)
    monkeypatch.setattr(
        main_entry.time, "sleep", lambda value: sleep_calls.append(value)
    )

    main_entry.main()

    download_dir = tmp_path / "ICML" / "2024"
    assert (
        download_dir / "Paper_One.pdf"
    ).read_bytes() == b"content:https://example.com/1.pdf"
    assert (
        download_dir / "Paper_Two.pdf"
    ).read_bytes() == b"content:https://example.com/2.pdf"

    with (tmp_path / "ICML_2024.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    assert rows == [
        ["Conference", "Year", "Filename", "Title", "Authors", "Category", "PDF_URL"],
        [
            "ICML",
            "2024",
            "Paper_One.pdf",
            "Paper One",
            "Alice",
            "C1",
            "https://example.com/1.pdf",
        ],
        [
            "ICML",
            "2024",
            "Paper_Two.pdf",
            "Paper Two",
            "Bob",
            "C2",
            "https://example.com/2.pdf",
        ],
    ]

    assert len(get_calls) == 2
    assert all(call[2] is True for call in get_calls)
    assert sleep_calls == [0, 0]
    assert "Total papers found: 2" in capsys.readouterr().out


def test_main_no_download_flag_skips_download_and_csv_rows(
    monkeypatch, tmp_path, capsys
):
    papers = [
        {
            "title": "P1",
            "authors": "A",
            "category": "C",
            "pdf_url": "https://example.com/1.pdf",
        },
        {
            "title": "P2",
            "authors": "B",
            "category": "C",
            "pdf_url": "https://example.com/2.pdf",
        },
    ]
    args = SimpleNamespace(
        conference="ICML",
        year="2024",
        save_dir=str(tmp_path),
        num_papers_to_download="-1",
        no_download_pdf=False,
        seconds_between_downloads="0",
    )

    monkeypatch.setattr(main_entry.command_args, "args", lambda _: args)
    monkeypatch.setattr(main_entry, "ICMLParser", lambda *_: _FakeParser(papers))
    monkeypatch.setattr(
        main_entry.generate_safe_filename,
        "generate_safe_filename",
        lambda _c, _y, title: f"{title}.pdf",
    )

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError(
            "requests.get should not be called when no_download_pdf is False"
        )

    monkeypatch.setattr(main_entry.requests, "get", fail_if_called)
    monkeypatch.setattr(main_entry.time, "sleep", lambda _value: None)

    main_entry.main()

    with (tmp_path / "ICML_2024.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    assert rows == [
        ["Conference", "Year", "Filename", "Title", "Authors", "Category", "PDF_URL"]
    ]
    assert "Papers Processed: 2" in capsys.readouterr().out


def test_main_logs_failed_download_and_continues(monkeypatch, tmp_path, capsys):
    papers = [
        {
            "title": "Broken",
            "authors": "A",
            "category": "C",
            "pdf_url": "https://example.com/broken.pdf",
        },
        {
            "title": "Working",
            "authors": "B",
            "category": "C",
            "pdf_url": "https://example.com/working.pdf",
        },
    ]
    args = SimpleNamespace(
        conference="ICML",
        year="2024",
        save_dir=str(tmp_path),
        num_papers_to_download="-1",
        no_download_pdf=True,
        seconds_between_downloads="0",
    )

    monkeypatch.setattr(main_entry.command_args, "args", lambda _: args)
    monkeypatch.setattr(main_entry, "ICMLParser", lambda *_: _FakeParser(papers))
    monkeypatch.setattr(
        main_entry.generate_safe_filename,
        "generate_safe_filename",
        lambda _c, _y, title: f"{title}.pdf",
    )

    responses = [
        pytest.raises,
        _FakeResponse([b"ok"]),
    ]

    def fake_get(url, headers, stream):
        del headers, stream
        item = responses.pop(0)
        if item is pytest.raises:
            raise main_entry.requests.exceptions.RequestException("boom")
        return item

    monkeypatch.setattr(main_entry.requests, "get", fake_get)
    monkeypatch.setattr(main_entry.time, "sleep", lambda _value: None)

    main_entry.main()

    failed_log = (tmp_path / "ICML" / "2024" / "failed_downloads.log").read_text(
        encoding="utf-8"
    )
    assert "Broken | https://example.com/broken.pdf | boom" in failed_log

    with (tmp_path / "ICML_2024.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    assert rows == [
        ["Conference", "Year", "Filename", "Title", "Authors", "Category", "PDF_URL"],
        [
            "ICML",
            "2024",
            "Working.pdf",
            "Working",
            "B",
            "C",
            "https://example.com/working.pdf",
        ],
    ]
    assert "Papers Processed: 1" in capsys.readouterr().out


def test_create_parser_for_jair_uses_static_directory(monkeypatch):
    captured = {}

    class FakeJAIRParser:
        def __init__(self, html_file_path, year):
            captured["html_file_path"] = html_file_path
            captured["year"] = year

    monkeypatch.setattr(main_entry, "JAIRParser", FakeJAIRParser)

    parser = main_entry._create_parser("JAIR", "2024")

    assert isinstance(parser, FakeJAIRParser)
    assert captured == {"html_file_path": "static_html/JAIR", "year": "2024"}


def test_create_parser_for_jmlr_uses_single_html_file(monkeypatch):
    captured = {}

    class FakeJMLRParser:
        def __init__(self, html_file_path, year):
            captured["html_file_path"] = html_file_path
            captured["year"] = year

    monkeypatch.setattr(main_entry, "JMLRParser", FakeJMLRParser)

    parser = main_entry._create_parser("JMLR", "2024")

    assert isinstance(parser, FakeJMLRParser)
    assert captured == {"html_file_path": "static_html/JMLR/2024.html", "year": "2024"}
