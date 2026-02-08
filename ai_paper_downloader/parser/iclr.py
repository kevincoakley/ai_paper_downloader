#!/usr/bin/env python

import openreview
from bs4 import BeautifulSoup
from bs4.element import Tag
import yaml


class ICLRParser:
    """Parse ICLR proceedings from OpenReview and legacy static HTML pages."""

    def __init__(self, html_file_path: str, year: str):
        self.html_file_path = html_file_path
        self.year = int(year)
        self.arxiv_base_url = "https://arxiv.org/pdf/"

    def parse_openreview(self) -> list[dict[str, str]]:
        """Parse ICLR submissions and accepted papers from OpenReview APIs."""
        with open("openreview_pass.yaml", "r", encoding="utf-8") as yamlfile:
            credentials = yaml.safe_load(yamlfile)

        if int(self.year) >= 2024:
            print("Using API V2")
            api_version = 2
            client = openreview.api.OpenReviewClient(
                baseurl="https://api2.openreview.net",
                username=credentials["username"],
                password=credentials["password"],
            )
        else:
            print("Using API V1")
            api_version = 1
            client = openreview.Client(
                baseurl="https://api.openreview.net",
                username=credentials["username"],
                password=credentials["password"],
            )

        if int(self.year) >= 2018:
            conference_id = f"ICLR.cc/{self.year}/Conference"
        else:
            conference_id = f"ICLR.cc/{self.year}/conference"

        if api_version == 2:
            # API v2 exposes accepted submissions via venue id.
            submissions = client.get_all_notes(content={"venueid": conference_id})
        elif api_version == 1:
            if int(self.year) >= 2018:
                submissions = client.get_all_notes(
                    invitation=f"{conference_id}/-/Blind_Submission",
                    details="directReplies",
                )
            else:
                submissions = client.get_notes(
                    invitation=f"{conference_id}/-/submission"
                )

        papers_metadata: list[dict[str, str]] = []

        for paper in submissions:
            if api_version == 2:
                title = paper.content.get("title", {}).get("value", "No title")
                authors = ", ".join(paper.content.get("authors", {}).get("value", []))
                venue = paper.content.get("venue", {}).get("value", "No venue")
                pdf_url = f"https://openreview.net/pdf?id={paper.id}"
            elif api_version == 1:
                title = paper.content.get("title", "No title")
                authors = ", ".join(paper.content.get("authors", []))
                venue = paper.content.get("venue", "No venue")
                pdf_url = f"https://openreview.net/pdf?id={paper.id}"

            category = "None"

            if api_version == 1 and int(self.year) == 2017:
                if "poster" in venue.lower():
                    category = "poster"
                elif "oral" in venue.lower():
                    category = "oral"
                elif "spotlight" in venue.lower():
                    category = "spotlight"
                elif "notable" in venue.lower():
                    category = "notable"
                elif "submitted" in venue.lower():
                    continue

            if api_version == 1 and int(self.year) >= 2018:
                for reply in paper.details["directReplies"]:
                    print(title)
                    if "/Acceptance_Decision" in reply["invitation"]:
                        category = reply["content"]["decision"]
                    if "/Decision" in reply["invitation"]:
                        category = reply["content"]["decision"]
                    if "/Meta_Review" in reply["invitation"]:
                        category = reply["content"]["recommendation"]

                if "reject" in category.lower():
                    continue
                elif category == "None":
                    print(f"Paper without category, skipping {title}")
                    continue

            if api_version == 2:
                category = venue

            papers_metadata.append(
                {
                    "title": title,
                    "authors": authors,
                    "category": category,
                    "pdf_url": pdf_url,
                }
            )

        return papers_metadata

    def parse_2015_2016(self) -> list[dict[str, str]]:
        """Parse 2015-2016 ICLR static pages with oral/poster sections."""
        with open(self.html_file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        papers_metadata: list[dict[str, str]] = []

        sections = {
            "Oral Presentations": "oral",
            "Poster Presentations": "poster",
            "Main Conference - Oral Presentations": "oral",
            "Main Conference - Poster Presentations": "poster",
        }

        for section_title, category in sections.items():
            section = soup.find("h3", string=section_title)
            if section:
                paper_list = section.find_next("ol")
                if paper_list:
                    for li in paper_list.find_all("li"):
                        li_tag = li if isinstance(li, Tag) else None
                        if li_tag is None:
                            continue

                        a = li_tag.find("a")
                        if a and "arxiv.org" in a["href"]:
                            arxiv_id = a["href"].split("/")[-1]
                            title = a.text.strip()
                            authors = li_tag.text.replace(title, "").strip()
                            authors = authors.replace("  ", " ")
                            authors = authors.replace("[code]\n", "")
                            authors = authors.removeprefix(", ")

                            papers_metadata.append(
                                {
                                    "title": title,
                                    "authors": authors,
                                    "category": category,
                                    "pdf_url": f"{self.arxiv_base_url}{arxiv_id}.pdf",
                                }
                            )

        return papers_metadata

    def parse_2014(self) -> list[dict[str, str]]:
        """Parse 2014 ICLR static HTML and assign oral/poster/workshop labels."""
        with open(self.html_file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        papers_metadata: list[dict[str, str]] = []
        seen_papers = set()

        oral_headers = ["Monday April 14:", "Tuesday April 15:", "Wednesday April 16:"]
        poster_header = "Conference Posters:"
        workshop_header = "Workshop Posters:"

        category = None
        active_session = None

        for elem in soup.find_all(["font", "p"]):
            text = elem.get_text().strip()
            link = elem.find("a", href=True)

            if elem.name == "font" and "size" in elem.attrs:
                font_size = elem["size"]
                if font_size == "5" and text in oral_headers:
                    active_session = "oral"
                    continue
                elif font_size == "4" and text == poster_header:
                    active_session = "poster"
                    continue
                elif font_size == "4" and text == workshop_header:
                    active_session = "workshop"
                    continue

            if link:
                title = link.get_text()
                url = link["href"]
                arxiv_id = url.split("/")[-1]

                authors_elem = elem.find_next_sibling("p")
                authors = authors_elem.get_text().strip() if authors_elem else "Unknown"

                paper_id = (title, authors, arxiv_id)

                if paper_id not in seen_papers:
                    seen_papers.add(paper_id)
                    papers_metadata.append(
                        {
                            "title": title,
                            "authors": authors,
                            "category": active_session if active_session else "unknown",
                            "pdf_url": f"{self.arxiv_base_url}{arxiv_id}.pdf",
                        }
                    )

        return papers_metadata

    def parse(self) -> list[dict[str, str]]:
        """Dispatch parsing by year and source format."""
        if self.year >= 2017:
            return self.parse_openreview()
        elif self.year == 2015 or self.year == 2016:
            return self.parse_2015_2016()
        elif self.year == 2014:
            return self.parse_2014()
        else:
            raise ValueError("Year not supported")
