#!/usr/bin/env python

from bs4 import BeautifulSoup
from bs4.element import Tag


class NeurIPSParser:
    """Parse NeurIPS proceedings HTML into normalized paper metadata."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)
        self.base_url = "https://proceedings.neurips.cc"

    def _build_pdf_url(self, relative_url: str) -> str:
        """Build a NeurIPS PDF URL from a proceedings abstract URL."""
        return self.base_url + relative_url.replace("hash", "file").replace(
            "-Abstract-Conference.html", "-Paper-Conference.pdf"
        ).replace(
            "-Abstract-Datasets_and_Benchmarks_Track.html",
            "-Paper-Datasets_and_Benchmarks_Track.pdf",
        ).replace(
            "-Abstract.html", "-Paper.pdf"
        )

    def _is_conference_paper(self, parent_li: Tag) -> bool:
        """Return whether a paper list item belongs to the main conference track."""
        return parent_li.get(
            "data-track"
        ) == "conference" or "conference" in parent_li.get("class", [])

    def _extract_authors(self, parent_li: Tag) -> str:
        """Extract authors from the HTML shape used for the configured year."""
        if self.year >= 2025:
            authors_tag = parent_li.find("span", class_="paper-authors")
        else:
            authors_tag = parent_li.find("i")

        return authors_tag.text.strip() if authors_tag else "Unknown"

    def parse(self) -> list[dict[str, str]]:
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        papers = soup.find_all("a", title="paper title")
        papers_metadata: list[dict[str, str]] = []

        for paper in papers:
            if not isinstance(paper, Tag):
                continue

            parent_li = paper.find_parent("li")
            if not parent_li:
                continue

            if not self._is_conference_paper(parent_li):
                continue

            title = paper.text.strip()
            authors = self._extract_authors(parent_li)
            pdf_url = self._build_pdf_url(str(paper["href"]))

            papers_metadata.append(
                {
                    "title": title,
                    "authors": authors,
                    "category": "conference",
                    "pdf_url": pdf_url,
                }
            )

        return papers_metadata
