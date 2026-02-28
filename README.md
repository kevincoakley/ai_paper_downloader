# ai_paper_downloader

A tool to download AI research papers from various AI conferences/journals (AAAI, DMLR, ICLR, ICML, IJCAI, JAIR, JMLR, NeurIPS, TMLR).

## Installation (with uv)

1. Install dependencies:
   ```sh
   uv sync
   ```

## Usage

Run with the script entrypoint:

```sh
uv run download_papers.py --conference DMLR --year 2025 --save-dir papers
```

See `uv run download_papers.py -h` for all available arguments.

## Testing

```sh
uv sync --group test
UV_CACHE_DIR=/tmp/uv-cache uv run pytest
UV_CACHE_DIR=/tmp/uv-cache uv run pytest --cov=.
UV_CACHE_DIR=/tmp/uv-cache uv run black .
```

## Notes
- For ICLR, you need an `openreview_pass.yaml` file with your OpenReview credentials.
- ICLR years 2024+ are parsed from static HTML files in `static_html/ICLR/`.
