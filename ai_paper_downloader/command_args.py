#!/usr/bin/env python

import argparse
from collections.abc import Sequence

CONFERENCE_CHOICES = ("AAAI", "ICLR", "ICML", "IJCAI", "NeurIPS")
YEAR_CHOICES = (
    "2024",
    "2023",
    "2022",
    "2021",
    "2020",
    "2019",
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
)


def _build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for paper download arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--conference",
        dest="conference",
        help="Conference name to download papers from",
        default="none",
        choices=CONFERENCE_CHOICES,
        required=True,
    )

    parser.add_argument(
        "--year",
        dest="year",
        help="Year of the conference",
        default="none",
        choices=YEAR_CHOICES,
        required=True,
    )

    parser.add_argument(
        "--save-dir",
        dest="save_dir",
        help="The directory to save the papers",
        default="papers",
        required=False,
    )

    parser.add_argument(
        "--num-papers-to-download",
        dest="num_papers_to_download",
        help="The number of papers to download",
        default=-1,
        required=False,
    )

    parser.add_argument(
        "--no-download-pdf",
        dest="no_download_pdf",
        help="Don't download the PDFs of the papers",
        action="store_false",
        required=False,
    )

    parser.add_argument(
        "--seconds-between-downloads",
        dest="seconds_between_downloads",
        help="The number of seconds to wait between downloading papers",
        default=1,
        required=False,
    )

    return parser


def args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    return _build_parser().parse_args(argv)
