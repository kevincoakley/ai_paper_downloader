#!/usr/bin/env python

import os
import re

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

YEAR_REGEX = re.compile(r"\b(19|20)\d{2}\b")


class TMLRParser:
    """Parse TMLR accepted-paper listings and filter by requested year."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)

    def _resolve_html_file_path(self) -> str:
        """Resolve the source HTML path from a file or known directory layout."""
        if os.path.isfile(self.html_file_path):
            return self.html_file_path

        candidates = ["all.html", "1.html", "index.html"]
        for candidate in candidates:
            candidate_path = os.path.join(self.html_file_path, candidate)
            if os.path.isfile(candidate_path):
                return candidate_path

        raise FileNotFoundError(f"No TMLR HTML file found in {self.html_file_path}")

    def _extract_year(self, paragraph: Tag, authors_tag: Tag) -> int | None:
        """Extract publication year from text between authors and line break."""
        date_text_parts: list[str] = []
        for sibling in authors_tag.next_siblings:
            sibling_tag = sibling if isinstance(sibling, Tag) else None
            if sibling_tag and sibling_tag.name == "br":
                break
            if isinstance(sibling, NavigableString):
                date_text_parts.append(str(sibling))

        date_text = " ".join(date_text_parts)
        match = YEAR_REGEX.search(date_text)
        if match:
            return int(match.group(0))

        fallback_match = YEAR_REGEX.search(paragraph.get_text(" ", strip=True))
        if fallback_match:
            return int(fallback_match.group(0))

        return None

    def parse(self) -> list[dict[str, str]]:
        """Parse TMLR HTML and return papers for the requested year only."""
        source_file_path = self._resolve_html_file_path()
        with open(source_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        papers_metadata: list[dict[str, str]] = []

        for item in soup.find_all("li", class_="item"):
            item_tag = item if isinstance(item, Tag) else None
            if item_tag is None:
                continue

            title_link = item_tag.find("a", class_="paper-data-bs-title")
            title = (
                title_link.get_text(strip=True) if isinstance(title_link, Tag) else ""
            )

            paragraph = item_tag.find("p")
            paragraph_tag = paragraph if isinstance(paragraph, Tag) else None
            if paragraph_tag is None:
                continue

            authors_tag = paragraph_tag.find("i")
            if not isinstance(authors_tag, Tag):
                continue
            authors = authors_tag.get_text(" ", strip=True)

            paper_year = self._extract_year(paragraph_tag, authors_tag)
            if paper_year != self.year:
                continue

            pdf_url = None
            for link in paragraph_tag.find_all("a", href=True):
                link_tag = link if isinstance(link, Tag) else None
                if link_tag is None:
                    continue
                if link_tag.get_text(strip=True).lower() == "pdf":
                    pdf_url = link_tag["href"]
                    break

            if not pdf_url:
                continue

            papers_metadata.append(
                {
                    "title": title,
                    "authors": authors,
                    "category": "",
                    "pdf_url": pdf_url,
                }
            )

        return papers_metadata
