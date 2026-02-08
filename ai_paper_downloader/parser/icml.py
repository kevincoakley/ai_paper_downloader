#!/usr/bin/env python

from bs4 import BeautifulSoup
from bs4.element import Tag


class ICMLParser:
    """Parse ICML proceedings HTML into normalized paper metadata."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)

    def parse(self) -> list[dict[str, str]]:
        """Parse ICML proceedings HTML into paper metadata records."""
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        papers = soup.find_all("div", class_="paper")
        papers_metadata: list[dict[str, str]] = []

        for paper in papers:
            paper_tag = paper if isinstance(paper, Tag) else None
            if paper_tag is None:
                continue

            title_tag = paper_tag.find("p", class_="title")
            title = title_tag.text.strip() if title_tag else "Unknown"

            authors_tag = paper_tag.find("span", class_="authors")
            authors = (
                authors_tag.text.strip().replace("\xa0", " ")
                if authors_tag
                else "Unknown"
            )

            pdf_link_tag = paper_tag.find("a", string="Download PDF")
            pdf_url = pdf_link_tag["href"] if pdf_link_tag else None

            category = "None"

            if not pdf_url:
                print(f"Skipping: No PDF found for {title}")
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
