from ai_paper_downloader.parser.tmlr import TMLRParser


def test_parse_filters_by_year_and_extracts_fields(tmp_path):
    html = """
    <html>
      <body>
        <ul>
          <li class="item nocertificate">
            <h4>
              <a class="paper-data-bs-title darkblue" href="https://openreview.net/pdf?id=C0yxuS6jty">
                <b>From Preferences to Prejudice</b>
              </a>
            </h4>
            <p>
              <i>Alice, Bob</i>, February 2026 <br>
              [<a href="https://openreview.net/forum?id=C0yxuS6jty">openreview</a>]
              [<a href="https://openreview.net/pdf?id=C0yxuS6jty">pdf</a>]
              [<a href="/tmlr/papers/bib/C0yxuS6jty.bib">bib</a>]
            </p>
          </li>
          <li class="item survey">
            <h4>
              <a class="paper-data-bs-title darkblue" href="https://openreview.net/pdf?id=oldpaper">
                <b>Older Paper</b>
              </a>
            </h4>
            <p>
              <i>Carol</i>, December 2025 <br>
              [<a href="https://openreview.net/forum?id=oldpaper">openreview</a>]
              [<a href="https://openreview.net/pdf?id=oldpaper">pdf</a>]
              [<a href="/tmlr/papers/bib/oldpaper.bib">bib</a>]
            </p>
          </li>
        </ul>
      </body>
    </html>
    """
    sample = tmp_path / "all.html"
    sample.write_text(html, encoding="utf-8")

    parser = TMLRParser(str(sample), "2026")

    assert parser.parse() == [
        {
            "title": "From Preferences to Prejudice",
            "authors": "Alice, Bob",
            "category": "",
            "pdf_url": "https://openreview.net/pdf?id=C0yxuS6jty",
        }
    ]


def test_parse_resolves_directory_input_with_fallback_filename(tmp_path):
    directory = tmp_path / "TMLR"
    directory.mkdir()
    (directory / "1.html").write_text(
        """
        <html>
          <body>
            <li class="item nocertificate">
              <h4><a class="paper-data-bs-title darkblue"><b>Dir Entry</b></a></h4>
              <p><i>Dan</i>, January 2024 <br>[<a href="https://openreview.net/pdf?id=dir">pdf</a>]</p>
            </li>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    parser = TMLRParser(str(directory), "2024")

    assert parser.parse() == [
        {
            "title": "Dir Entry",
            "authors": "Dan",
            "category": "",
            "pdf_url": "https://openreview.net/pdf?id=dir",
        }
    ]
