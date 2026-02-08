# ai_paper_downloader

A tool to download AI research papers from various AI conferences (AAAI, ICLR, ICML, IJCAI, NeurIPS).

## Installation (with uv)

1. Install dependencies:
   ```sh
   uv sync
   ```

## Usage

Run the package as a module with the required arguments. Example:

```sh
uv run python -m ai_paper_downloader --conference ICLR --year 2014 --save-dir papers
```

See `uv run python -m ai_paper_downloader -h` for all available arguments.

## Notes
- For ICLR, you need an `openreview_pass.yaml` file with your OpenReview credentials.