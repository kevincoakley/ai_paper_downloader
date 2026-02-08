from ai_paper_downloader.parser.neurips import NeurIPSParser


def test_parse_builds_categories_and_pdf_urls(tmp_path):
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
          <li>
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
        {
            "title": "Data Paper",
            "authors": "Bob",
            "category": "datasets_and_benchmarks_track",
            "pdf_url": "https://proceedings.neurips.cc/file/b-Paper-Datasets_and_Benchmarks_Track.pdf",
        },
        {
            "title": "General Paper",
            "authors": "Carol",
            "category": "None",
            "pdf_url": "https://proceedings.neurips.cc/file/c-Paper.pdf",
        },
    ]
