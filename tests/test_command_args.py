from ai_paper_downloader import command_args


def test_args_defaults():
    parsed = command_args.args(["--conference", "ICML", "--year", "2024"])

    assert parsed.conference == "ICML"
    assert parsed.year == "2024"
    assert parsed.save_dir == "papers"
    assert parsed.num_papers_to_download == -1
    assert parsed.no_download_pdf is True
    assert parsed.seconds_between_downloads == 1


def test_no_download_pdf_flag_sets_false():
    parsed = command_args.args(
        ["--conference", "NeurIPS", "--year", "2023", "--no-download-pdf"]
    )

    assert parsed.no_download_pdf is False
