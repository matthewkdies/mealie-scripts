# Mealie Scripts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

A CLI tool for interacting with and automating tasks on a [Mealie](https://mealie.io/) instance.

## Roadmap

This project is under active development. For more information, see the [roadmap](./ROADMAP.md).

## Features

- **Recipes Management**: Automate tagging of recipes based on nutritional information (`check-macros`) or total time (`check-quick`).
- **Tags**: List all tags available on the Mealie instance.
- **Cache Management**: Inspect and clear local caches used by commands.
- **Debug**: Test connections and view current CLI configuration.

## Disclaimer

This project is not officially associated with or endorsed by [Mealie](https://mealie.io/). This CLI is primarily intended for use with automation tasks, such as cron jobs, to manage your Mealie instance programmatically.

## Development

This project uses `prek` to ensure code quality.

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (for dependency management)
- `prek` (for running hooks)

### Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Install pre-commit hooks:
   ```bash
   pre install -t pre-commit -t pre-push
   ```
