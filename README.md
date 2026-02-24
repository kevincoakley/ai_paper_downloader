# ai_paper_downloader

A tool to download AI research papers from various AI conferences/journals (AAAI, ICLR, ICML, IJCAI, JAIR, JMLR, NeurIPS, TMLR).

## Installation (with uv)

1. Install dependencies:
   ```sh
   uv sync
   ```

## Usage

Run with the script entrypoint:

```sh
uv run download_papers.py --conference TMLR --year 2026 --save-dir papers
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
