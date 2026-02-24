from ai_paper_downloader.parser.dmlr import DMLRParser


def test_parse_reads_all_files_and_filters_requested_year(tmp_path):
    (tmp_path / "1.html").write_text(
        """
        <html>
          <body>
            <h1 class="post-title">Volume 1</h1>
            <li class="list-group-item">
              <dt>Paper One</dt>
              <dd>
                <b><i>Alice</i></b>, <b><i>Bob</i></b>, (1):1-10, 2024.
              </dd>
              <a href="/assets/pdf/v01-1.pdf">[PDF]</a>
            </li>
            <li class="list-group-item">
              <dt>Paper Two</dt>
              <dd>
                <b><i>Carol</i></b>, (2):1-12, 2025.
              </dd>
              <a href="/assets/pdf/v01-2.pdf">[PDF]</a>
            </li>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    (tmp_path / "2.html").write_text(
        """
        <html>
          <body>
            <h1 class="post-title">Volume 2</h1>
            <li class="list-group-item">
              <dt>Paper Three</dt>
              <dd>
                <b><i>Dan</i></b>, <b><i>Eve</i></b>, (3):1-20, 2024.
              </dd>
              <a href="https://data.mlr.press/assets/pdf/v02-3.pdf">[PDF]</a>
            </li>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    parser = DMLRParser(str(tmp_path), "2024")

    assert parser.parse() == [
        {
            "title": "Paper One",
            "authors": "Alice, Bob",
            "category": "Volume 1",
            "pdf_url": "https://data.mlr.press/assets/pdf/v01-1.pdf",
        },
        {
            "title": "Paper Three",
            "authors": "Dan, Eve",
            "category": "Volume 2",
            "pdf_url": "https://data.mlr.press/assets/pdf/v02-3.pdf",
        },
    ]


def test_parse_handles_single_file_input(tmp_path):
    sample = tmp_path / "single.html"
    sample.write_text(
        """
        <html>
          <body>
            <h1 class="post-title">Volume 9</h1>
            <li class="list-group-item">
              <dt>Single File Paper</dt>
              <dd><b><i>Frank</i></b>, (1):1-5, 2025.</dd>
              <a href="/assets/pdf/v09-1.pdf">[PDF]</a>
            </li>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    parser = DMLRParser(str(sample), "2025")

    assert parser.parse() == [
        {
            "title": "Single File Paper",
            "authors": "Frank",
            "category": "Volume 9",
            "pdf_url": "https://data.mlr.press/assets/pdf/v09-1.pdf",
        }
    ]
