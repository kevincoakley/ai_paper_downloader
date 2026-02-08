# AGENTS.md

> Purpose: This file provides context, conventions, and setup instructions for AI agents working on this repository.

## 1. Project Overview
- Description: This repository contains scripts to download the PDF of papers from various AI conferences & journals using static HTML files of the proceedings or OpenReview.
- Language: Python
- Package Manager: `uv` (Do not use pip or poetry directly)

## 2. Directory Structure

```
.
├── .gitignore                    # Git ignore file
├── .python-version               # Python version file
├── AGENTS.md                     # This file
├── ai_paper_downloader           # Main package directory
│   ├── __init__.py               # Package initializer
│   ├── __main__.py               # Main entry point for command-line execution
│   ├── command_args.py           # Argument parsing for command-line interface
│   ├── generate_safe_filename.py # Utility for generating unique and safe filenames
│   ├── main_entry.py             # Main script for downloading papers
│   └── parser                    # Subpackage for conference-specific parsers
│       ├── __init__.py           # Subpackage initializer
│       ├── aaai.py               # Parser for AAAI conference
│       ├── iclr.py               # Parser for ICLR conference
│       ├── icml.py               # Parser for ICML conference
│       ├── ijcai.py              # Parser for IJCAI conference
│       └── neurips.py            # Parser for NeurIPS conference
├── download_papers.py            # Script to run the paper downloading process
├── openreview_pass.yaml          # YAML file for OpenReview credentials (required for ICLR)
├── papers/                       # Directory where downloaded papers will be saved
├── pyproject.toml                # Project configuration
├── README.md                     # Project description
├── static_html
│   ├── AAAI/                     # Directory of static HTML from the proceedings of the AAAI conference
│   ├── ICLR/                     # Directory of static HTML from the proceedings of the ICLR conference
│   ├── ICML/                     # Directory of static HTML from the proceedings of the ICML conference
│   ├── IJCAI/                    # Directory of static HTML from the proceedings of the IJCAI conference
│   └── NeurIPS/                  # Directory of static HTML from the proceedings of the NeurIPS conference
├── tests/                        # Directory for test files
└── uv.lock                       # Lock file for dependencies
```

## 3. Development Workflow & Commands
Always use `uv` for package management and script execution.

### Setup
- First time setup: `uv sync` (Installs environment based on lockfile)
- Update environment: `uv sync`

### Dependency Management
- Add production dependency: `uv add <package_name>`
- Add dev/test dependency: `uv add <package_name> --group test`
- Remove dependency: `uv remove <package_name>`

### Running Code
- Run script: `uv run python <script_path>`

### Testing
- Install test environment: `uv sync --group test`
- Run all tests: `uv run pytest`
- Write tests for new features
- Maintain existing test coverage
- Use pytest fixtures for common setup
- Create separate test files for each module
- Create test in a `tests/` directory at the root level
- Name test files as `test_<module>.py`
- Test coverage: `uv run pytest --cov=.`

## Development Workflow
1. Write/update tests first (TDD approach)
2. Implement changes
3. Run tests to ensure they pass
4. Format code with Black

## 4. Coding Conventions & Style

### Formatting
- Formatter: Black
  - Command: `uv run black .`
  - Rule: Always run formatting before declaring a task complete.
- Follow PEP 8 conventions
- Use type hints where appropriate
- Write docstrings for functions and classes

### Commenting
- Use clear and concise comments to explain non-obvious code

### Type Hinting
- Use standard Python type hints for function arguments and return values.
- Example: `def my_func(name: str) -> int:`

## 5. Critical Rules for Agents
- Do not update `uv.lock` manually. Use `uv add` or `uv sync`.
- Check `pyproject.toml` to see existing dependencies before adding new ones.
- Run tests after every significant code change to ensure no regressions.
- Ensure code is formatted with Black
- Preserve existing code style and patterns
- Aways update the README.md file with instructions for running the code. Be concise, don't include unnecessary information. Focus on how to run the code for testing.
- Ask for clarification if requirements are unclear
