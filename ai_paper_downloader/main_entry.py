import csv
import os
import sys
import time
from argparse import Namespace
from typing import Any, TextIO

import requests

from ai_paper_downloader import command_args
from ai_paper_downloader import generate_safe_filename
from ai_paper_downloader.parser.aaai import AAAIParser
from ai_paper_downloader.parser.iclr import ICLRParser
from ai_paper_downloader.parser.icml import ICMLParser
from ai_paper_downloader.parser.ijcai import IJCAIParser
from ai_paper_downloader.parser.jair import JAIRParser
from ai_paper_downloader.parser.jmlr import JMLRParser
from ai_paper_downloader.parser.neurips import NeurIPSParser

CSV_FIELDS = [
    "Conference",
    "Year",
    "Filename",
    "Title",
    "Authors",
    "Category",
    "PDF_URL",
]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)


def _print_run_banner(args: Namespace) -> None:
    """Print a consistent run banner for CLI output."""
    print("========================================================================")
    print(
        f"Conference: {args.conference} Year: {args.year} Save Directory: {args.save_dir}"
    )
    print("========================================================================")


def _build_output_paths(args: Namespace) -> tuple[str, str]:
    """Build output directory and CSV file paths from parsed arguments."""
    download_path = f"{args.save_dir}/{args.conference}/{args.year}"
    csv_file_path = f"{args.save_dir}/{args.conference}_{args.year}.csv"
    return download_path, csv_file_path


def _create_parser(conference: str, year: str) -> Any:
    """Create the conference-specific parser instance for the requested year."""
    if conference == "AAAI":
        return AAAIParser(f"static_html/{conference}", year)
    if conference == "JAIR":
        return JAIRParser(f"static_html/{conference}", year)

    html_file_path = f"static_html/{conference}/{year}.html"
    parser_map = {
        "ICLR": ICLRParser,
        "ICML": ICMLParser,
        "IJCAI": IJCAIParser,
        "JMLR": JMLRParser,
        "NeurIPS": NeurIPSParser,
    }
    return parser_map[conference](html_file_path, year)


def _download_and_record(
    args: Namespace,
    paper: dict[str, str],
    safe_filename: str,
    pdf_file_path: str,
    count: int,
    num_papers_to_download: str | int,
    csv_writer: Any,
    csv_file: TextIO,
    failed_log: TextIO,
) -> bool:
    """Download a PDF and append one CSV row, returning success status."""
    if os.path.exists(pdf_file_path):
        print(f"Skipping (already exists): {pdf_file_path}")
        return False

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(paper["pdf_url"], headers=headers, stream=True)
        response.raise_for_status()

        with open(pdf_file_path, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)

        print(
            f"[{count + 1}/{num_papers_to_download}] Downloaded: {paper['title']} -> {pdf_file_path}"
        )

        csv_writer.writerow(
            [
                args.conference,
                args.year,
                safe_filename,
                paper["title"],
                paper["authors"],
                paper["category"],
                paper["pdf_url"],
            ]
        )
        csv_file.flush()

        time.sleep(int(args.seconds_between_downloads))
    except requests.exceptions.RequestException as error:
        print(f"Failed to download {paper['title']}: {error}")
        failed_log.write(f"{paper['title']} | {paper['pdf_url']} | {error}\n")
        failed_log.flush()
        return False

    return True


def main() -> None:
    """Run the paper parsing and download pipeline from CLI arguments."""
    args = command_args.args(sys.argv[1:])
    _print_run_banner(args)

    download_path, csv_file_path = _build_output_paths(args)
    os.makedirs(download_path, exist_ok=True)

    parser = _create_parser(args.conference, args.year)
    papers = parser.parse()

    total_papers = len(papers)
    print(f"Total papers found: {total_papers}")

    if int(args.num_papers_to_download) != -1:
        num_papers_to_download = args.num_papers_to_download
    else:
        num_papers_to_download = total_papers

    write_headers = not os.path.exists(csv_file_path)
    failed_log_path = os.path.join(download_path, "failed_downloads.log")

    with (
        open(csv_file_path, mode="a", newline="", encoding="utf-8") as csv_file,
        open(failed_log_path, "a", encoding="utf-8") as failed_log,
    ):
        csv_writer = csv.writer(csv_file)

        if write_headers:
            csv_writer.writerow(CSV_FIELDS)

        count = 0

        for paper in papers:
            safe_filename = generate_safe_filename.generate_safe_filename(
                args.conference, args.year, paper["title"]
            )
            pdf_file_path = f"{download_path}/{safe_filename}"

            if args.no_download_pdf:
                downloaded = _download_and_record(
                    args,
                    paper,
                    safe_filename,
                    pdf_file_path,
                    count,
                    num_papers_to_download,
                    csv_writer,
                    csv_file,
                    failed_log,
                )
                if not downloaded:
                    continue

            count += 1

            if int(args.num_papers_to_download) != -1:
                if count >= int(num_papers_to_download):
                    break

    print("========================================================================")
    print(f"Papers Processed: {count}")
    print("========================================================================")
