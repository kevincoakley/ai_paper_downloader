import runpy
from pathlib import Path

from ai_paper_downloader import main_entry


def test_download_papers_script_invokes_main(monkeypatch):
    called = []

    def fake_main():
        called.append(True)

    monkeypatch.setattr(main_entry, "main", fake_main)

    script_path = Path(__file__).resolve().parents[1] / "download_papers.py"
    runpy.run_path(str(script_path), run_name="__main__")

    assert called == [True]
