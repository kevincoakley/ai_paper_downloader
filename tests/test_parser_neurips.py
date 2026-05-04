from ai_paper_downloader.parser.neurips import NeurIPSParser


def test_parse_2024_layout_extracts_conference_papers_only(tmp_path):
    html = """
    <html>
      <body>
        <ul>
          <li class="conference">
            <a title="paper title" href="/hash/a-Abstract-Conference.html">Conf Paper</a>
            <i>Alice</i>
          </li>
          <li class="datasets_and_benchmarks_track">
            <a title="paper title" href="/hash/b-Abstract-Datasets_and_Benchmarks_Track.html">Data Paper</a>
            <i>Bob</i>
          </li>
          <li class="position_paper_track">
            <a title="paper title" href="/hash/c-Abstract.html">General Paper</a>
            <i>Carol</i>
          </li>
        </ul>
      </body>
    </html>
    """
    sample = tmp_path / "neurips.html"
    sample.write_text(html, encoding="utf-8")

    parser = NeurIPSParser(str(sample), "2024")

    assert parser.parse() == [
        {
            "title": "Conf Paper",
            "authors": "Alice",
            "category": "conference",
            "pdf_url": "https://proceedings.neurips.cc/file/a-Paper-Conference.pdf",
        },
    ]


def test_parse_2025_layout_extracts_conference_papers_only(tmp_path):
    html = """
    <html>
      <body>
        <ul class="paper-list">
          <li class="conference" data-track="conference">
            <div class="paper-content">
              <a title="paper title" href="/paper_files/paper/2025/hash/a-Abstract-Conference.html">Conf Paper</a>
              <span class="paper-authors">Alice, Alex</span>
            </div>
            <span class="paper-track-badge">Main Conference Track</span>
          </li>
          <li class="datasets_and_benchmarks_track" data-track="datasets_and_benchmarks_track">
            <div class="paper-content">
              <a title="paper title" href="/paper_files/paper/2025/hash/b-Abstract-Datasets_and_Benchmarks_Track.html">Data Paper</a>
              <span class="paper-authors">Bob</span>
            </div>
            <span class="paper-track-badge">Datasets and Benchmarks Track</span>
          </li>
          <li class="position_paper_track" data-track="position_paper_track">
            <div class="paper-content">
              <a title="paper title" href="/paper_files/paper/2025/hash/c-Abstract.html">Position Paper</a>
              <span class="paper-authors">Carol</span>
            </div>
            <span class="paper-track-badge">Position Paper Track</span>
          </li>
        </ul>
      </body>
    </html>
    """
    sample = tmp_path / "neurips.html"
    sample.write_text(html, encoding="utf-8")

    parser = NeurIPSParser(str(sample), "2025")

    assert parser.parse() == [
        {
            "title": "Conf Paper",
            "authors": "Alice, Alex",
            "category": "conference",
            "pdf_url": "https://proceedings.neurips.cc/paper_files/paper/2025/file/a-Paper-Conference.pdf",
        },
    ]


def test_parse_2026_uses_2025_plus_layout(tmp_path):
    html = """
    <html>
      <body>
        <ul class="paper-list">
          <li class="conference" data-track="conference">
            <div class="paper-content">
              <a title="paper title" href="/paper_files/paper/2026/hash/a-Abstract-Conference.html">Future Conf Paper</a>
              <span class="paper-authors">Dana</span>
            </div>
          </li>
        </ul>
      </body>
    </html>
    """
    sample = tmp_path / "neurips.html"
    sample.write_text(html, encoding="utf-8")

    parser = NeurIPSParser(str(sample), "2026")

    assert parser.parse() == [
        {
            "title": "Future Conf Paper",
            "authors": "Dana",
            "category": "conference",
            "pdf_url": "https://proceedings.neurips.cc/paper_files/paper/2026/file/a-Paper-Conference.pdf",
        },
    ]
