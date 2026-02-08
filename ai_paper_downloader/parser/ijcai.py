#!/usr/bin/env python

import os

from bs4 import BeautifulSoup
from bs4.element import Tag

MAIN_TRACK_CATEGORY = "Main Track"
UNKNOWN_VALUE = "Unknown"
IJCAI_BASE_URL = "https://www.ijcai.org"


class IJCAIParser:
    """Parse IJCAI proceedings pages across old and new site layouts."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)

    def _build_proceedings_url(self, href: str) -> str:
        """Resolve relative IJCAI PDF links against the year proceedings URL."""
        if href.startswith("http"):
            return href
        return os.path.join(f"{IJCAI_BASE_URL}/proceedings/{self.year}/", href)

    def _extract_old_style_paper(self, paragraph: Tag) -> dict[str, str] | None:
        """Extract title/authors/pdf from one old-style IJCAI paragraph block."""
        contents = paragraph.contents
        if len(contents) < 5:
            return None
        if not isinstance(contents[0], str):
            return None

        title_part = contents[0].strip()
        title = title_part.split("/")[0].strip() if "/" in title_part else title_part

        authors = "Unknown"
        for content in contents:
            if getattr(content, "name", None) == "em":
                authors = content.get_text(strip=True)
                break
        if authors == "Unknown":
            for content in contents:
                if getattr(content, "name", None) == "i":
                    authors = content.get_text(strip=True)
                    break

        pdf_url = None
        for link in paragraph.find_all("a"):
            if link.get_text(strip=True).upper() == "PDF" and link.get("href"):
                href = link["href"]
                if href.startswith("http"):
                    pdf_url = href
                else:
                    pdf_url = f"{IJCAI_BASE_URL}{href}"
                break

        if not pdf_url or not title or not authors:
            return None

        return {
            "title": title,
            "authors": authors,
            "pdf_url": pdf_url,
        }

    def _extract_new_style_papers(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        """Extract metadata from the section/subsection-based IJCAI layout."""
        papers_metadata: list[dict[str, str]] = []
        for section in soup.find_all("div", class_="section"):
            if not isinstance(section, Tag):
                continue

            section_title_div = section.find("div", class_="section_title")
            if section_title_div and section_title_div.find("h3"):
                track_name = section_title_div.find("h3").get_text(strip=True)
            else:
                track_name = UNKNOWN_VALUE

            for subsection in section.find_all("div", class_="subsection"):
                if not isinstance(subsection, Tag):
                    continue

                subsection_title_div = subsection.find("div", class_="subsection_title")
                category = (
                    subsection_title_div.get_text(strip=True)
                    if subsection_title_div
                    else track_name
                )

                for paper in subsection.find_all("div", class_="paper_wrapper"):
                    if not isinstance(paper, Tag):
                        continue

                    title_tag = paper.find("div", class_="title")
                    title = (
                        title_tag.get_text(strip=True) if title_tag else UNKNOWN_VALUE
                    )

                    authors_tag = paper.find("div", class_="authors")
                    authors = (
                        authors_tag.get_text(strip=True)
                        if authors_tag
                        else UNKNOWN_VALUE
                    )

                    details_div = paper.find("div", class_="details")
                    pdf_url = None
                    if details_div:
                        pdf_link = details_div.find("a", string="PDF")
                        if pdf_link and pdf_link.get("href"):
                            pdf_url = self._build_proceedings_url(pdf_link["href"])

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

    def _extract_old_style_papers(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        """Extract metadata from the legacy IJCAI heading/paragraph layout."""
        papers_metadata: list[dict[str, str]] = []
        last_category = None
        collecting = False

        for tag in soup.find_all(["h3", "p"]):
            if not isinstance(tag, Tag):
                continue

            if tag.name == "h3":
                title = tag.get_text(strip=True)
                title_lower = title.lower()
                if (
                    title_lower.startswith("edited by")
                    or "sponsor" in title_lower
                    or "published by" in title_lower
                ):
                    continue
                last_category = title
                collecting = True
                continue

            paper = self._extract_old_style_paper(tag)
            if paper is None:
                continue

            category = (
                MAIN_TRACK_CATEGORY
                if not collecting or not last_category
                else last_category
            )
            papers_metadata.append(
                {
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "category": category,
                    "pdf_url": paper["pdf_url"],
                }
            )

        return papers_metadata

    def _deduplicate_by_pdf_url(
        self, papers_metadata: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Keep first occurrence of each paper keyed by PDF URL."""
        unique: dict[str, dict[str, str]] = {}
        for paper in papers_metadata:
            key = paper["pdf_url"]
            if key not in unique:
                unique[key] = paper
        return list(unique.values())

    def parse(self) -> list[dict[str, str]]:
        """Parse IJCAI HTML and return deduplicated paper metadata."""
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        sections = soup.find_all("div", class_="section")
        if sections:
            papers_metadata = self._extract_new_style_papers(soup)
        else:
            papers_metadata = self._extract_old_style_papers(soup)

        return self._deduplicate_by_pdf_url(papers_metadata)
