from ai_paper_downloader.parser.aaai import AAAIParser


def test_parse_legacy_layout_extracts_category_authors_and_pdf(tmp_path):
    html = """
    <html>
      <body>
        <div class="track-wrap"><h2>Main Track</h2></div>
        <li class="paper-wrap">
          <h5>Paper One</h5>
          <span class="papers-author-page">Alice, Bob</span>
          <a class="wp-block-button" href="https://example.com/p1.pdf">PDF</a>
        </li>
      </body>
    </html>
    """
    sample = tmp_path / "sample.html"
    sample.write_text(html, encoding="utf-8")

    parser = AAAIParser(str(tmp_path), "2020")
    parser.html_files[2020] = ["sample.html"]

    assert parser.parse() == [
        {
            "title": "Paper One",
            "authors": "Alice, Bob",
            "category": "Main Track",
            "pdf_url": "https://example.com/p1.pdf",
        }
    ]


def test_parse_modern_layout_extracts_section_articles(tmp_path):
    html = """
    <html>
      <body>
        <div class="section">
          <h2>Reinforcement Learning</h2>
          <div class="obj_article_summary">
            <h3 class="title"><a>Modern Paper</a></h3>
            <div class="authors">Carol</div>
            <a class="obj_galley_link pdf" href="https://example.com/modern.pdf">PDF</a>
          </div>
        </div>
      </body>
    </html>
    """
    sample = tmp_path / "sample-2023.html"
    sample.write_text(html, encoding="utf-8")

    parser = AAAIParser(str(tmp_path), "2023")
    parser.html_files[2023] = ["sample-2023.html"]

    assert parser.parse() == [
        {
            "title": "Modern Paper",
            "authors": "Carol",
            "category": "Reinforcement Learning",
            "pdf_url": "https://example.com/modern.pdf",
        }
    ]
