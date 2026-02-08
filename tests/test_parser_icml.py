from ai_paper_downloader.parser.icml import ICMLParser


def test_parse_extracts_papers_and_skips_missing_pdf(tmp_path, capsys):
    html = """
    <html>
      <body>
        <div class="paper">
          <p class="title">Paper With PDF</p>
          <span class="authors">Alice\xa0Bob</span>
          <a href="https://example.com/paper.pdf">Download PDF</a>
        </div>
        <div class="paper">
          <p class="title">Paper Without PDF</p>
          <span class="authors">Carol</span>
        </div>
      </body>
    </html>
    """
    sample = tmp_path / "icml.html"
    sample.write_text(html, encoding="utf-8")

    parser = ICMLParser(str(sample), "2024")
    parsed = parser.parse()

    assert parsed == [
        {
            "title": "Paper With PDF",
            "authors": "Alice Bob",
            "category": "None",
            "pdf_url": "https://example.com/paper.pdf",
        }
    ]
    assert "Skipping: No PDF found for Paper Without PDF" in capsys.readouterr().out
