from ai_paper_downloader.parser.ijcai import IJCAIParser


def test_parse_new_style_extracts_and_deduplicates(tmp_path):
    html = """
    <html>
      <body>
        <div class="section">
          <div class="section_title"><h3>Main Track</h3></div>
          <div class="subsection">
            <div class="subsection_title">NLP</div>
            <div class="paper_wrapper">
              <div class="title">Paper One</div>
              <div class="authors">Alice</div>
              <div class="details"><a href="papers/1.pdf">PDF</a></div>
            </div>
            <div class="paper_wrapper">
              <div class="title">Paper One Duplicate</div>
              <div class="authors">Alice</div>
              <div class="details"><a href="papers/1.pdf">PDF</a></div>
            </div>
          </div>
          <div class="subsection">
            <div class="paper_wrapper">
              <div class="title">Paper Two</div>
              <div class="authors">Bob</div>
              <div class="details"><a href="https://cdn.example.com/2.pdf">PDF</a></div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    sample = tmp_path / "2024.html"
    sample.write_text(html, encoding="utf-8")

    parser = IJCAIParser(str(sample), "2024")

    assert parser.parse() == [
        {
            "title": "Paper One",
            "authors": "Alice",
            "category": "NLP",
            "pdf_url": "https://www.ijcai.org/proceedings/2024/papers/1.pdf",
        },
        {
            "title": "Paper Two",
            "authors": "Bob",
            "category": "Main Track",
            "pdf_url": "https://cdn.example.com/2.pdf",
        },
    ]


def test_parse_old_style_handles_main_track_and_h3_categories(tmp_path):
    html = """
    <html>
      <body>
        <p>Pre-H3 Paper / extra <em>Alice</em> , <a href="/proceedings/2015/1.pdf">PDF</a> .</p>
        <h3>Reasoning</h3>
        <p>Category Paper / extra <i>Bob</i> , <a href="/proceedings/2015/2.pdf">PDF</a> .</p>
      </body>
    </html>
    """
    sample = tmp_path / "2015.html"
    sample.write_text(html, encoding="utf-8")

    parser = IJCAIParser(str(sample), "2015")

    assert parser.parse() == [
        {
            "title": "Pre-H3 Paper",
            "authors": "Alice",
            "category": "Main Track",
            "pdf_url": "https://www.ijcai.org/proceedings/2015/1.pdf",
        },
        {
            "title": "Category Paper",
            "authors": "Bob",
            "category": "Reasoning",
            "pdf_url": "https://www.ijcai.org/proceedings/2015/2.pdf",
        },
    ]
