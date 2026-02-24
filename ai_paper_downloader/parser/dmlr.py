#!/usr/bin/env python

import re
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag

DMLR_BASE_URL = "https://data.mlr.press"
YEAR_REGEX = re.compile(r",\s*(19|20)\d{2}\.")


class DMLRParser:
    """Parse DMLR volume HTML files and filter papers by requested year."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)

    def _resolve_pdf_url(self, href: str) -> str:
        """Resolve DMLR PDF link to an absolute URL."""
        if href.startswith("http://") or href.startswith("https://"):
            return href
        if href.startswith("/"):
            return f"{DMLR_BASE_URL}{href}"
        return f"{DMLR_BASE_URL}/{href}"

    def _extract_year(self, details: Tag) -> int | None:
        """Extract publication year from the paper details text."""
        details_text = details.get_text(" ", strip=True)
        match = YEAR_REGEX.search(details_text)
        if not match:
            return None
        return int(match.group(0).split(",")[-1].replace(".", "").strip())

    def _parse_volume_file(self, html_path: Path) -> list[dict[str, str]]:
        """Parse one DMLR volume file and return matching-year papers."""
        with html_path.open("r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        category_tag = soup.find("h1", class_="post-title")
        category = (
            category_tag.get_text(" ", strip=True)
            if isinstance(category_tag, Tag)
            else "Unknown"
        )

        papers_metadata: list[dict[str, str]] = []
        for item in soup.find_all("li", class_="list-group-item"):
            item_tag = item if isinstance(item, Tag) else None
            if item_tag is None:
                continue

            title_tag = item_tag.find("dt")
            title = (
                title_tag.get_text(" ", strip=True)
                if isinstance(title_tag, Tag)
                else ""
            )

            details_tag = item_tag.find("dd")
            if not isinstance(details_tag, Tag):
                continue

            parsed_year = self._extract_year(details_tag)
            if parsed_year != self.year:
                continue

            author_tags = details_tag.find_all("i")
            authors = ", ".join(
                author.get_text(" ", strip=True)
                for author in author_tags
                if isinstance(author, Tag) and author.get_text(strip=True)
            )

            pdf_url = None
            for link in item_tag.find_all("a", href=True):
                link_tag = link if isinstance(link, Tag) else None
                if link_tag is None:
                    continue
                if link_tag.get_text(strip=True).lower() == "[pdf]":
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

    def parse(self) -> list[dict[str, str]]:
        """Parse all DMLR volume files and return papers for the selected year."""
        base_path = Path(self.html_file_path)
        if base_path.is_file():
            html_files = [base_path]
        elif base_path.is_dir():
            html_files = sorted(base_path.glob("*.html"))
        else:
            raise FileNotFoundError(f"No such file or directory: {self.html_file_path}")

        papers_metadata: list[dict[str, str]] = []
        for html_file in html_files:
            papers_metadata.extend(self._parse_volume_file(html_file))

        return papers_metadata
