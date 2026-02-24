#!/usr/bin/env python

from bs4 import BeautifulSoup
from bs4.element import Tag

JAIR_BASE_URL = "https://www.jair.org"


class JAIRParser:
    """Parse JAIR issue HTML files into normalized paper metadata."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)
        self.html_files = {
            supported_year: [
                f"{supported_year}-1.html",
                f"{supported_year}-2.html",
                f"{supported_year}-3.html",
            ]
            for supported_year in range(2014, 2026)
        }

    def _normalize_pdf_url(self, href: str) -> str:
        """Convert JAIR view links to direct-download PDF links."""
        resolved_href = href
        if resolved_href.startswith("/"):
            resolved_href = f"{JAIR_BASE_URL}{resolved_href}"
        return resolved_href.replace("/view/", "/download/", 1)

    def _extract_pdf_url(self, article: Tag) -> str | None:
        """Extract the primary PDF link from one article summary block."""
        pdf_links = article.find_all("a", class_="galley-link")
        for link in pdf_links:
            link_tag = link if isinstance(link, Tag) else None
            if link_tag is None:
                continue
            classes = link_tag.get("class", [])
            href = link_tag.get("href")
            if "pdf" in classes and href and link_tag.get_text(strip=True) == "PDF":
                return self._normalize_pdf_url(href)

        for link in pdf_links:
            link_tag = link if isinstance(link, Tag) else None
            if link_tag is None:
                continue
            classes = link_tag.get("class", [])
            href = link_tag.get("href")
            if "pdf" in classes and href:
                return self._normalize_pdf_url(href)

        return None

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract the issue volume label from breadcrumb active item."""
        active_tag = soup.find("li", class_="active")
        if not isinstance(active_tag, Tag):
            return "Unknown"
        return active_tag.get_text(" ", strip=True)

    def _parse_issue(self, issue_file_path: str) -> list[dict[str, str]]:
        """Parse one JAIR issue HTML file."""
        with open(issue_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        category = self._extract_category(soup)
        papers_metadata: list[dict[str, str]] = []

        for article in soup.find_all("div", class_="article-summary"):
            article_tag = article if isinstance(article, Tag) else None
            if article_tag is None:
                continue

            heading = article_tag.find("h3", class_="media-heading")
            title_anchor = heading.find("a") if isinstance(heading, Tag) else None
            title = title_anchor.get_text(strip=True) if title_anchor else "Unknown"

            authors_tag = article_tag.find("div", class_="authors")
            authors = (
                authors_tag.get_text(" ", strip=True)
                if isinstance(authors_tag, Tag)
                else "Unknown"
            )

            pdf_url = self._extract_pdf_url(article_tag)
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

    def parse(self) -> list[dict[str, str]]:
        """Parse all JAIR issue files for the selected year."""
        if self.year not in self.html_files:
            raise ValueError("Year not supported")

        papers_metadata: list[dict[str, str]] = []
        for issue_file in self.html_files[self.year]:
            issue_file_path = f"{self.html_file_path}/{issue_file}"
            papers_metadata.extend(self._parse_issue(issue_file_path))
        return papers_metadata
