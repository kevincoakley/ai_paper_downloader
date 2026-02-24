import pytest

from ai_paper_downloader.parser.jair import JAIRParser


def test_parse_extracts_volume_category_and_download_pdf_urls(tmp_path):
    (tmp_path / "2024-1.html").write_text(
        """
        <html>
          <body>
            <li class="active">Vol. 79 (2024)</li>
            <div class="article-summary media">
              <h3 class="media-heading">
                <a href="https://www.jair.org/index.php/jair/article/view/1">Paper One</a>
              </h3>
              <div class="authors">Alice, Bob</div>
              <a class="galley-link btn btn-primary pdf" href="https://www.jair.org/index.php/jair/article/view/1/10001">PDF</a>
            </div>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    (tmp_path / "2024-2.html").write_text(
        """
        <html>
          <body>
            <li class="active">Vol. 80 (2024)</li>
            <div class="article-summary media">
              <h3 class="media-heading">
                <a href="https://www.jair.org/index.php/jair/article/view/2">Paper Two</a>
              </h3>
              <div class="authors">Carol</div>
              <a class="galley-link btn btn-primary pdf" href="https://www.jair.org/index.php/jair/article/view/2/10002">PDF</a>
              <a class="galley-link btn btn-primary pdf" href="https://www.jair.org/index.php/jair/article/view/2/10003">Online Appendices</a>
            </div>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    (tmp_path / "2024-3.html").write_text(
        """
        <html>
          <body>
            <li class="active">Vol. 81 (2024)</li>
            <div class="article-summary media">
              <h3 class="media-heading"><a href="https://www.jair.org/index.php/jair/article/view/3">Missing PDF</a></h3>
              <div class="authors">Ignored</div>
            </div>
            <div class="article-summary media">
              <h3 class="media-heading"><a href="https://www.jair.org/index.php/jair/article/view/4">Paper Three</a></h3>
              <div class="authors">Dan</div>
              <a class="galley-link btn btn-primary pdf" href="/index.php/jair/article/view/4/10004">PDF</a>
            </div>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    parser = JAIRParser(str(tmp_path), "2024")

    assert parser.parse() == [
        {
            "title": "Paper One",
            "authors": "Alice, Bob",
            "category": "Vol. 79 (2024)",
            "pdf_url": "https://www.jair.org/index.php/jair/article/download/1/10001",
        },
        {
            "title": "Paper Two",
            "authors": "Carol",
            "category": "Vol. 80 (2024)",
            "pdf_url": "https://www.jair.org/index.php/jair/article/download/2/10002",
        },
        {
            "title": "Paper Three",
            "authors": "Dan",
            "category": "Vol. 81 (2024)",
            "pdf_url": "https://www.jair.org/index.php/jair/article/download/4/10004",
        },
    ]


def test_parse_raises_for_unsupported_year(tmp_path):
    parser = JAIRParser(str(tmp_path), "2013")

    with pytest.raises(ValueError, match="Year not supported"):
        parser.parse()
