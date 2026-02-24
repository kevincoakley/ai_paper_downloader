from ai_paper_downloader.parser.jmlr import JMLRParser


def test_parse_extracts_volume_category_and_absolute_pdf_urls(tmp_path):
    html = """
    <html>
      <body>
        <h1>JMLR Volume 25</h1>
        <dl>
          <dt>First Paper</dt>
          <dd>
            <b><i>Alice, Bob</i></b>
            <br>
            [<a href='/papers/v25/first.html'>abs</a>]
            [<a href='/papers/volume25/first/first.pdf'>pdf</a>]
          </dd>
        </dl>
        <dl>
          <dt>Second Paper</dt>
          <dd>
            <b><i>Carol</i></b>
            <br>
            [<a href='/papers/v25/second.html'>abs</a>]
            [<a href='https://jmlr.org/papers/volume25/second/second.pdf'>pdf</a>]
          </dd>
        </dl>
      </body>
    </html>
    """
    sample = tmp_path / "2024.html"
    sample.write_text(html, encoding="utf-8")

    parser = JMLRParser(str(sample), "2024")

    assert parser.parse() == [
        {
            "title": "First Paper",
            "authors": "Alice, Bob",
            "category": "JMLR Volume 25",
            "pdf_url": "https://jmlr.org/papers/volume25/first/first.pdf",
        },
        {
            "title": "Second Paper",
            "authors": "Carol",
            "category": "JMLR Volume 25",
            "pdf_url": "https://jmlr.org/papers/volume25/second/second.pdf",
        },
    ]


def test_parse_skips_entries_without_pdf(tmp_path):
    html = """
    <html>
      <body>
        <h1>JMLR Volume 24</h1>
        <dl>
          <dt>Paper Without PDF</dt>
          <dd><b><i>Ignored</i></b> [<a href='/papers/v24/nope.html'>abs</a>]</dd>
        </dl>
      </body>
    </html>
    """
    sample = tmp_path / "2023.html"
    sample.write_text(html, encoding="utf-8")

    parser = JMLRParser(str(sample), "2023")

    assert parser.parse() == []
