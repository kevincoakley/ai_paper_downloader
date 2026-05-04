from ai_paper_downloader import command_args


def test_args_defaults():
    parsed = command_args.args(["--conference", "ICML", "--year", "2024"])

    assert parsed.conference == "ICML"
    assert parsed.year == "2024"
    assert parsed.save_dir == "papers"
    assert parsed.num_papers_to_download == -1
    assert parsed.no_download_pdf is False
    assert parsed.seconds_between_downloads == 0


def test_no_download_pdf_flag_sets_true():
    parsed = command_args.args(
        ["--conference", "NeurIPS", "--year", "2023", "--no-download-pdf"]
    )

    assert parsed.no_download_pdf is True


def test_jair_is_supported_conference_choice():
    parsed = command_args.args(["--conference", "JAIR", "--year", "2024"])

    assert parsed.conference == "JAIR"


def test_jmlr_is_supported_conference_choice():
    parsed = command_args.args(["--conference", "JMLR", "--year", "2024"])

    assert parsed.conference == "JMLR"


def test_tmlr_is_supported_conference_choice():
    parsed = command_args.args(["--conference", "TMLR", "--year", "2026"])

    assert parsed.conference == "TMLR"
    assert parsed.year == "2026"


def test_dmlr_is_supported_conference_choice():
    parsed = command_args.args(["--conference", "DMLR", "--year", "2025"])

    assert parsed.conference == "DMLR"
