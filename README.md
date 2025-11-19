# webscraping_CE_EU

Python utilities that scrape the [European Circular Economy Stakeholder Platform](https://circulareconomy.europa.eu/platform/en/good-practices) for published good-practice case studies and generate quick visual summaries of the collected data. The repository currently contains a scraper that walks through the paginated directory, normalizes each listing into a tabular dataset, and an analysis helper that produces count plots for the categorical attributes.

## Repository contents
- `scrape_ce.py` &mdash; pulls listing cards from every page, extracts a consistent set of attributes, and saves them into `good_practices.csv`.
- `analyze.py` &mdash; reads the CSV output and stores distribution plots for each major column in `plots/`.
- `plots/` &mdash; destination folder for generated images; populated after running `analyze.py`.

Each scraped record contains the following fields:

| Column | Description |
| --- | --- |
| `Title` | Title of the good-practice entry on the platform. |
| `Description` | Short abstract/summary provided by the publisher. |
| `Link` | Canonical URL on the Circular Economy site. |
| `Organisation` | Reporting organisation/company. |
| `Type of Organisation` | Contributor category as classified by the platform. |
| `Country` | Country associated with the practice. |
| `Language` | Main language of the published material. |
| `Key Area` | Platform key area tags (comma-separated when multiple apply). |
| `Sector` | Listed sectors (comma-separated). |
| `Scope` | Geographic scope tags (comma-separated). |

## Requirements
- Python 3.9+ with `pip`
- Install dependencies via:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage
1. **Scrape the dataset**
   ```bash
   python scrape_ce.py
   ```
   - The script automatically loops through every paginated listing until an empty page is reached (hard stop at page 80 to avoid infinite loops).
   - Command-line flags let you change retries, delays, destination file, and more (see [CLI reference](#cli-reference)).
   - Output: `good_practices.csv` in the repository root by default.

2. **Generate quick visualizations**
   ```bash
   python analyze.py
   ```
   - Creates the `plots/` folder if it does not exist.
   - Saves one horizontal count plot per categorical column requested through `--columns` (defaults match the column table above). Each file is named `<Column>_distribution.png`.

### CLI reference
| Script | Useful flags |
| --- | --- |
| `scrape_ce.py` | `--output <path>` choose another CSV destination; `--max-pages <n>` limit crawl depth; `--skip-page <n>` skip specific page numbers (repeatable flag); `--retries`/`--delay` tune retry policy; `--log-level DEBUG` increase verbosity. |
| `analyze.py` | `--input <csv>` point to another dataset; `--output-dir <folder>` control where charts go; `--columns Country Language ...` limit the generated plots; `--log-level DEBUG` for troubleshooting. |

### Testing
Automated tests cover the parsing logic and plot generation helpers. Run them with:
```bash
pytest
```

## Notes and tips
- Respect the website's traffic limits. The CLI exposes `--delay` and `--retries` so you can slow down the crawl for politeness.
- Inspect `good_practices.csv` before sharing: it contains the full description text from the site.
- If the platform's markup changes, update the CSS selectors inside `get_good_practices` accordingly.
- Both scripts log progress and warnings to stdout/stderr. Use `--log-level DEBUG` for detailed traces or review the messages to diagnose failed pages.

## License
Distributed under the terms of the MIT License. See `LICENSE` for details.
