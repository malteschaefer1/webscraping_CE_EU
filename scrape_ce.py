"""Scrape the Circular Economy EU platform for registered good-practice entries."""

from __future__ import annotations

import argparse
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Set

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

LOGGER = logging.getLogger(__name__)

BASE_DOMAIN = "https://circulareconomy.europa.eu"
BASE_URL = f"{BASE_DOMAIN}/platform/en/good-practices"
DEFAULT_MAX_PAGES = 80
REQUEST_TIMEOUT = 10
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


@dataclass
class GoodPractice:
    """Structured representation of a single good-practice listing."""

    title: str = "N/A"
    description: str = "N/A"
    link: str = "N/A"
    organisation: str = "N/A"
    type_of_organisation: str = "N/A"
    country: str = "N/A"
    language: str = "N/A"
    key_area: str = "N/A"
    sector: str = "N/A"
    scope: str = "N/A"

    def to_row(self) -> dict:
        """Return the record using the column names expected by the dataset."""
        return {
            "Title": self.title,
            "Description": self.description,
            "Link": self.link,
            "Organisation": self.organisation,
            "Type of Organisation": self.type_of_organisation,
            "Country": self.country,
            "Language": self.language,
            "Key Area": self.key_area,
            "Sector": self.sector,
            "Scope": self.scope,
        }


def parse_practice_card(practice: Tag) -> GoodPractice:
    """Extract the fields for a single practice card."""
    title_tag = practice.find("h2")
    title = title_tag.get_text(strip=True) if title_tag else "N/A"
    link = title_tag.find("a")["href"] if title_tag and title_tag.find("a") else ""
    full_link = f"{BASE_DOMAIN}{link}" if link.startswith("/") else link or "N/A"

    description_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-abstract "
        "field-name-field-cecon-abstract field-type-text-long field-label-hidden",
    )
    description = description_tag.get_text(strip=True) if description_tag else "N/A"

    organization_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-organisation-company "
        "field-name-field-cecon-organisation-company field-type-link field-label-above",
    )
    organization = (
        organization_tag.find("a").get_text(strip=True)
        if organization_tag and organization_tag.find("a")
        else "N/A"
    )

    type_of_org_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-contributor-category "
        "field-name-field-cecon-contributor-category field-type-entity-reference field-label-above",
    )
    type_of_org = (
        type_of_org_tag.find("a").get_text(strip=True)
        if type_of_org_tag and type_of_org_tag.find("a")
        else "N/A"
    )

    country_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-country "
        "field-name-field-cecon-country field-type-country field-label-above",
    )
    country = (
        country_tag.find("div", class_="field-item").get_text(strip=True)
        if country_tag
        else "N/A"
    )

    language_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-main-language "
        "field-name-field-cecon-main-language field-type-entity-reference field-label-above",
    )
    language = (
        language_tag.find("a").get_text(strip=True)
        if language_tag and language_tag.find("a")
        else "N/A"
    )

    key_area_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-key-area "
        "field-name-field-cecon-key-area field-type-entity-reference field-label-above",
    )
    key_area = (
        ", ".join(a.get_text(strip=True) for a in key_area_tag.find_all("a"))
        if key_area_tag
        else "N/A"
    )

    sector_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-sector "
        "field-name-field-cecon-sector field-type-entity-reference field-label-above",
    )
    sector = (
        ", ".join(a.get_text(strip=True) for a in sector_tag.find_all("a"))
        if sector_tag
        else "N/A"
    )

    scope_tag = practice.find(
        "div",
        class_="field-wrapper field field-node--field-cecon-scope "
        "field-name-field-cecon-scope field-type-entity-reference field-label-above",
    )
    scope = (
        ", ".join(a.get_text(strip=True) for a in scope_tag.find_all("a"))
        if scope_tag
        else "N/A"
    )

    return GoodPractice(
        title=title,
        description=description,
        link=full_link,
        organisation=organization,
        type_of_organisation=type_of_org,
        country=country,
        language=language,
        key_area=key_area,
        sector=sector,
        scope=scope,
    )


def parse_practices(html: str) -> List[GoodPractice]:
    """Parse the provided HTML fragment and return all practice records."""
    soup = BeautifulSoup(html, "html.parser")
    practices = soup.find_all("div", class_="node--type-cecon-good-practice")
    LOGGER.debug("Found %s practice cards in the HTML fragment.", len(practices))
    return [parse_practice_card(practice) for practice in practices]


def get_good_practices(
    session: requests.Session,
    page_url: str,
    retries: int = 3,
    delay: int = 5,
) -> List[GoodPractice]:
    """Fetch a listing page and extract structured data for each practice card."""
    for attempt in range(1, retries + 1):
        LOGGER.info("Fetching URL %s (attempt %s/%s)", page_url, attempt, retries)
        try:
            response = session.get(page_url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                LOGGER.warning(
                    "Unexpected status code %s while requesting %s",
                    response.status_code,
                    page_url,
                )
            else:
                LOGGER.debug("Successfully retrieved %s", page_url)
                return parse_practices(response.text)
        except requests.RequestException as exc:
            LOGGER.error("Request error on %s: %s", page_url, exc)

        if attempt < retries:
            LOGGER.info("Retrying in %s seconds...", delay)
            time.sleep(delay)

    LOGGER.error("Failed to retrieve data from %s after %s attempts.", page_url, retries)
    return []


def scrape_all_pages(
    session: requests.Session,
    base_url: str = BASE_URL,
    max_pages: int = DEFAULT_MAX_PAGES,
    skip_pages: Iterable[int] | None = None,
    retries: int = 3,
    delay: int = 5,
) -> List[GoodPractice]:
    """Iterate through paginated results until a page has no data or the cap is hit."""
    skip: Set[int] = set(skip_pages or [])
    all_data: List[GoodPractice] = []
    page = 0

    while page < max_pages:
        if page in skip:
            LOGGER.info("Skipping page %s as requested.", page)
            page += 1
            continue

        page_url = f"{base_url}?page={page}"
        page_data = get_good_practices(session, page_url, retries=retries, delay=delay)
        if not page_data:
            LOGGER.warning("No data returned for page %s. Stopping pagination.", page)
            break

        all_data.extend(page_data)
        LOGGER.info("Page %s scraped. Total records: %s", page, len(all_data))
        page += 1

    return all_data


def write_dataset(records: Sequence[GoodPractice], output_path: Path) -> None:
    """Persist the scraped records into a CSV file."""
    if not records:
        raise ValueError("No records available to write.")

    df = pd.DataFrame([record.to_row() for record in records])
    output_path = output_path.expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    LOGGER.info("Saved %s records to %s", len(df), output_path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape the Circular Economy EU good practices directory."
    )
    parser.add_argument(
        "--output",
        default="good_practices.csv",
        help="Path to the CSV output (default: %(default)s).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help="Maximum number of pages to crawl (default: %(default)s).",
    )
    parser.add_argument(
        "--skip-page",
        dest="skip_pages",
        action="append",
        type=int,
        default=[],
        help=(
            "Page number to skip (0-indexed). "
            "Provide multiple --skip-page flags to skip several pages."
        ),
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries per page before giving up (default: %(default)s).",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=5,
        help="Delay in seconds between retries (default: %(default)s).",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Override the base listing URL (default: %(default)s).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity (default: %(default)s).",
    )
    return parser.parse_args(argv)


def configure_logging(level: str) -> None:
    """Configure application-wide logging once."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point when executing the module as a script."""
    args = parse_args(argv)
    configure_logging(args.log_level)

    LOGGER.info("Starting the scraping process.")
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    records = scrape_all_pages(
        session=session,
        base_url=args.base_url,
        max_pages=args.max_pages,
        skip_pages=args.skip_pages,
        retries=args.retries,
        delay=args.delay,
    )

    if not records:
        LOGGER.error("Scraping completed but produced no records.")
        return 1

    try:
        write_dataset(records, Path(args.output))
    except (OSError, ValueError) as exc:
        LOGGER.error("Failed to persist dataset: %s", exc)
        return 2

    LOGGER.info("Scraping finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
