#!/usr/bin/env python

from bs4 import BeautifulSoup
from bs4.element import Tag

JMLR_BASE_URL = "https://jmlr.org"


class JMLRParser:
    """Parse JMLR volume HTML files into normalized paper metadata."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract the volume label from the top-level heading."""
        heading = soup.find("h1")
        if not isinstance(heading, Tag):
            return "Unknown"
        return heading.get_text(" ", strip=True)

    def _resolve_pdf_url(self, href: str) -> str:
        """Resolve relative JMLR PDF links against the site domain."""
        if href.startswith("http://") or href.startswith("https://"):
            return href
        if href.startswith("/"):
            return f"{JMLR_BASE_URL}{href}"
        return f"{JMLR_BASE_URL}/{href}"

    def parse(self) -> list[dict[str, str]]:
        """Parse JMLR HTML into paper metadata records."""
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        category = self._extract_category(soup)
        papers_metadata: list[dict[str, str]] = []

        for paper in soup.find_all("dl"):
            paper_tag = paper if isinstance(paper, Tag) else None
            if paper_tag is None:
                continue

            title_tag = paper_tag.find("dt")
            title = title_tag.get_text(strip=True) if isinstance(title_tag, Tag) else ""

            details_tag = paper_tag.find("dd")
            details = details_tag if isinstance(details_tag, Tag) else None
            authors_tag = details.find("i") if details else None
            authors = (
                authors_tag.get_text(" ", strip=True)
                if isinstance(authors_tag, Tag)
                else ""
            )

            pdf_url = None
            if details:
                for link in details.find_all("a", href=True):
                    link_tag = link if isinstance(link, Tag) else None
                    if link_tag is None:
                        continue
                    if link_tag.get_text(strip=True).lower() == "pdf":
                        pdf_url = self._resolve_pdf_url(link_tag["href"])
                        break

            if not pdf_url:
                continue

            papers_metadata.append(
                {
                    "title": title,
                    "authors": authors,
                    "category": category,
                    "pdf_url": pdf_url,
                }
            )

        return papers_metadata
