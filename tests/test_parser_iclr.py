import pytest

from ai_paper_downloader.parser.iclr import ICLRParser


def test_parse_2015_2016_extracts_arxiv_papers(tmp_path):
    html = """
    <html>
      <body>
        <h3>Oral Presentations</h3>
        <ol>
          <li><a href="https://arxiv.org/abs/1234.5678">Oral Title</a>, Alice</li>
        </ol>
        <h3>Poster Presentations</h3>
        <ol>
          <li><a href="https://arxiv.org/abs/9999.0001">Poster Title</a>, Bob</li>
        </ol>
      </body>
    </html>
    """
    sample = tmp_path / "2015.html"
    sample.write_text(html, encoding="utf-8")

    parser = ICLRParser(str(sample), "2015")

    assert parser.parse_2015_2016() == [
        {
            "title": "Oral Title",
            "authors": "Alice",
            "category": "oral",
            "pdf_url": "https://arxiv.org/pdf/1234.5678.pdf",
        },
        {
            "title": "Poster Title",
            "authors": "Bob",
            "category": "poster",
            "pdf_url": "https://arxiv.org/pdf/9999.0001.pdf",
        },
    ]


def test_parse_2014_extracts_session_and_deduplicates(tmp_path):
    html = """
    <html>
      <body>
        <font size="5">Monday April 14:</font>
        <p><a href="https://arxiv.org/abs/1111.1111">Paper One</a></p>
        <p>Alice, Bob</p>
        <p><a href="https://arxiv.org/abs/1111.1111">Paper One</a></p>
        <p>Alice, Bob</p>
        <font size="4">Conference Posters:</font>
        <p><a href="https://arxiv.org/abs/2222.2222">Paper Two</a></p>
        <p>Carol</p>
      </body>
    </html>
    """
    sample = tmp_path / "2014.html"
    sample.write_text(html, encoding="utf-8")

    parser = ICLRParser(str(sample), "2014")

    assert parser.parse_2014() == [
        {
            "title": "Paper One",
            "authors": "Alice, Bob",
            "category": "oral",
            "pdf_url": "https://arxiv.org/pdf/1111.1111.pdf",
        },
        {
            "title": "Paper Two",
            "authors": "Carol",
            "category": "poster",
            "pdf_url": "https://arxiv.org/pdf/2222.2222.pdf",
        },
    ]


def test_parse_dispatch_by_year(monkeypatch, tmp_path):
    sample = tmp_path / "sample.html"
    sample.write_text("<html></html>", encoding="utf-8")

    parser_2024 = ICLRParser(str(sample), "2024")
    monkeypatch.setattr(parser_2024, "parse_2024_plus", lambda: ["2024_plus"])
    assert parser_2024.parse() == ["2024_plus"]

    parser_2018 = ICLRParser(str(sample), "2018")
    monkeypatch.setattr(parser_2018, "parse_openreview", lambda: ["openreview"])
    assert parser_2018.parse() == ["openreview"]

    parser_2016 = ICLRParser(str(sample), "2016")
    monkeypatch.setattr(parser_2016, "parse_2015_2016", lambda: ["2015_2016"])
    assert parser_2016.parse() == ["2015_2016"]

    parser_2014 = ICLRParser(str(sample), "2014")
    monkeypatch.setattr(parser_2014, "parse_2014", lambda: ["2014"])
    assert parser_2014.parse() == ["2014"]


def test_parse_2024_plus_extracts_and_transforms_static_links(tmp_path):
    html = """
    <html>
      <body>
        <ul>
          <li class="conference">
            <a title="paper title" href="/paper_files/paper/2025/hash/000eba875068854d5ff003b1fa534cd6-Abstract-Conference.html">
              Generalization and Distributed Learning of GFlowNets
            </a>
            <i>Tiago Silva, Amauri Souza, Omar Rivasplata, Vikas Garg, Samuel Kaski, Diego Mesquita</i>
          </li>
        </ul>
      </body>
    </html>
    """
    sample = tmp_path / "2025.html"
    sample.write_text(html, encoding="utf-8")

    parser = ICLRParser(str(sample), "2025")

    assert parser.parse_2024_plus() == [
        {
            "title": "Generalization and Distributed Learning of GFlowNets",
            "authors": "Tiago Silva, Amauri Souza, Omar Rivasplata, Vikas Garg, Samuel Kaski, Diego Mesquita",
            "category": "",
            "pdf_url": "https://proceedings.iclr.cc/paper_files/paper/2025/file/000eba875068854d5ff003b1fa534cd6-Paper-Conference.pdf",
        }
    ]


def test_parse_raises_for_unsupported_year(tmp_path):
    sample = tmp_path / "sample.html"
    sample.write_text("<html></html>", encoding="utf-8")

    parser = ICLRParser(str(sample), "2013")

    with pytest.raises(ValueError, match="Year not supported"):
        parser.parse()
