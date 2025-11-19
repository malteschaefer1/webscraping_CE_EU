"""Quick exploratory plots for the scraped Circular Economy dataset."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

import pandas as pd

LOGGER = logging.getLogger(__name__)

DEFAULT_COLUMNS = [
    "Organisation",
    "Type of Organisation",
    "Country",
    "Language",
    "Key Area",
    "Sector",
    "Scope",
]


def load_dataset(csv_path: Path) -> pd.DataFrame:
    """Load the scraped CSV dataset, raising a descriptive error if missing."""
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Could not find dataset at {csv_path}. Run scrape_ce.py first."
        ) from exc


def ensure_directory(path: Path) -> None:
    """Ensure the output directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def save_bar_plot(df: pd.DataFrame, column: str, filename: Path) -> None:
    """Create and save a horizontal count plot for the provided column."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(10, 6))
    sns.countplot(y=column, data=df, order=df[column].value_counts().index)
    plt.title(f"Distribution of {column}")
    plt.xlabel("Count")
    plt.ylabel(column)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    LOGGER.info("Saved %s", filename)


def generate_plots(
    df: pd.DataFrame, columns: Sequence[str], output_dir: Path
) -> None:
    """Generate and persist plots for selected columns."""
    ensure_directory(output_dir)
    for column in columns:
        if column not in df.columns:
            LOGGER.warning("Column '%s' not present in dataset. Skipping.", column)
            continue
        filename = output_dir / f"{column}_distribution.png"
        save_bar_plot(df, column, filename)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the analysis helper."""
    parser = argparse.ArgumentParser(
        description="Generate exploratory plots for the scraped dataset."
    )
    parser.add_argument(
        "--input",
        default="good_practices.csv",
        help="Path to the scraped CSV dataset (default: %(default)s).",
    )
    parser.add_argument(
        "--output-dir",
        default="plots",
        help="Folder where generated plots will be stored (default: %(default)s).",
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        default=DEFAULT_COLUMNS,
        help="List of columns to visualize (default: %(default)s).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity (default: %(default)s).",
    )
    return parser.parse_args(argv)


def configure_logging(level: str) -> None:
    """Configure logging for CLI usage."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for CLI execution."""
    args = parse_args(argv)
    configure_logging(args.log_level)

    csv_path = Path(args.input).expanduser()
    output_dir = Path(args.output_dir).expanduser()

    try:
        df = load_dataset(csv_path)
    except FileNotFoundError as exc:
        LOGGER.error(exc)
        return 1

    generate_plots(df, args.columns, output_dir)
    LOGGER.info("Plots have been saved in %s", output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
