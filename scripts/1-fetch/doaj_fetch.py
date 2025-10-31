#!/usr/bin/env python
"""
Fetch DOAJ journals with CC license information and generate count reports.
Note: DOAJ articles don't contain license information in their API.
"""
# Standard library
import argparse
import csv
import os
import sys
import textwrap
import time
import traceback
from collections import Counter, defaultdict

# Third-party
import requests
import yaml
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonTracebackLexer
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add parent directory so shared can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# First-party/Local
import shared  # noqa: E402

# Setup
LOGGER, PATHS = shared.setup(__file__)

# Constants
BASE_URL = "https://doaj.org/api/v3/search"
DEFAULT_FETCH_LIMIT = 1000
RATE_LIMIT_DELAY = 0.5

# CSV Headers
HEADER_COUNT = ["TOOL_IDENTIFIER", "COUNT"]
HEADER_SUBJECT_REPORT = [
    "TOOL_IDENTIFIER",
    "SUBJECT_CODE",
    "SUBJECT_LABEL",
    "COUNT",
]
HEADER_LANGUAGE = ["TOOL_IDENTIFIER", "LANGUAGE_CODE", "LANGUAGE", "COUNT"]
HEADER_YEAR = ["TOOL_IDENTIFIER", "YEAR", "COUNT"]

# CC License types
CC_LICENSE_TYPES = [
    "CC BY",
    "CC BY-NC",
    "CC BY-SA",
    "CC BY-ND",
    "CC BY-NC-SA",
    "CC BY-NC-ND",
    "CC0",
    "UNKNOWN CC legal tool",
]

# Language code to readable name mapping
LANGUAGE_NAMES = {
    "EN": "English",
    "ES": "Spanish",
    "PT": "Portuguese",
    "FR": "French",
    "DE": "German",
    "IT": "Italian",
    "RU": "Russian",
    "ZH": "Chinese",
    "JA": "Japanese",
    "AR": "Arabic",
    "TR": "Turkish",
    "NL": "Dutch",
    "SV": "Swedish",
    "NO": "Norwegian",
    "DA": "Danish",
    "FI": "Finnish",
    "PL": "Polish",
    "CS": "Czech",
    "HU": "Hungarian",
    "RO": "Romanian",
    "BG": "Bulgarian",
    "HR": "Croatian",
    "SK": "Slovak",
    "SL": "Slovenian",
    "ET": "Estonian",
    "LV": "Latvian",
    "LT": "Lithuanian",
    "EL": "Greek",
    "CA": "Catalan",
    "IS": "Icelandic",
    "MK": "Macedonian",
    "SR": "Serbian",
    "UK": "Ukrainian",
    "BE": "Belarusian",
    "KO": "Korean",
    "TH": "Thai",
    "VI": "Vietnamese",
    "ID": "Indonesian",
    "MS": "Malay",
    "HI": "Hindi",
    "BN": "Bengali",
    "UR": "Urdu",
    "FA": "Persian",
    "HE": "Hebrew",
    "SW": "Swahili",
    "AF": "Afrikaans",
}

# File Paths
FILE_DOAJ_COUNT = shared.path_join(PATHS["data_1-fetch"], "doaj_1_count.csv")
FILE_DOAJ_SUBJECT_REPORT = shared.path_join(
    PATHS["data_1-fetch"], "doaj_2_count_by_subject_report.csv"
)
FILE_DOAJ_LANGUAGE = shared.path_join(
    PATHS["data_1-fetch"], "doaj_3_count_by_language.csv"
)
FILE_DOAJ_YEAR = shared.path_join(
    PATHS["data_1-fetch"], "doaj_4_count_by_year.csv"
)
FILE_PROVENANCE = shared.path_join(
    PATHS["data_1-fetch"], "doaj_provenance.yaml"
)

# Runtime variables
QUARTER = os.path.basename(PATHS["data_quarter"])


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch DOAJ journals with CC licenses"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_FETCH_LIMIT,
        help=f"Total journals to fetch (default: {DEFAULT_FETCH_LIMIT})",
    )
    parser.add_argument(
        "--enable-save",
        action="store_true",
        help="Enable saving data to CSV files",
    )
    parser.add_argument(
        "--enable-git", action="store_true", help="Enable git actions"
    )
    args = parser.parse_args()
    if not args.enable_save and args.enable_git:
        parser.error("--enable-git requires --enable-save")
    return args


def setup_session():
    """Setup requests session with retry strategy."""
    retry_strategy = Retry(
        total=5, backoff_factor=1, status_forcelist=shared.STATUS_FORCELIST
    )
    session = requests.Session()
    session.headers.update({"User-Agent": shared.USER_AGENT})
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    return session


def initialize_data_file(file_path, headers):
    """Initialize CSV file with headers if it doesn't exist."""
    if not os.path.isfile(file_path):
        with open(file_path, "w", encoding="utf-8", newline="\n") as file_obj:
            writer = csv.DictWriter(
                file_obj, fieldnames=headers, dialect="unix"
            )
            writer.writeheader()


def initialize_all_data_files(args):
    """Initialize all data files."""
    if not args.enable_save:
        return
    os.makedirs(PATHS["data_1-fetch"], exist_ok=True)
    initialize_data_file(FILE_DOAJ_COUNT, HEADER_COUNT)
    initialize_data_file(FILE_DOAJ_SUBJECT_REPORT, HEADER_SUBJECT_REPORT)
    initialize_data_file(FILE_DOAJ_LANGUAGE, HEADER_LANGUAGE)
    initialize_data_file(FILE_DOAJ_YEAR, HEADER_YEAR)


def extract_license_type(license_info):
    """Extract CC license type from DOAJ license information."""
    if not license_info:
        return "UNKNOWN CC legal tool"
    for lic in license_info:
        lic_type = lic.get("type", "")
        if lic_type in CC_LICENSE_TYPES:
            return lic_type
    return "UNKNOWN CC legal tool"


def process_journals(session, args):
    """Process DOAJ journals with CC licenses."""
    LOGGER.info("Fetching DOAJ journals...")

    license_counts = Counter()
    subject_counts = defaultdict(Counter)
    language_counts = defaultdict(Counter)
    year_counts = defaultdict(Counter)

    total_processed = 0
    page = 1
    page_size = 100

    while total_processed < args.limit:
        LOGGER.info(f"Fetching journals page {page}...")

        url = f"{BASE_URL}/journals/*"
        params = {"pageSize": page_size, "page": page}

        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Failed to fetch journals page {page}: {e}")
            break

        results = data.get("results", [])
        if not results:
            break

        for journal in results:
            if total_processed >= args.limit:
                break

            bibjson = journal.get("bibjson", {})

            # Check for CC license
            license_info = bibjson.get("license")
            if not license_info:
                continue

            license_type = extract_license_type(license_info)
            if license_type == "UNKNOWN CC legal tool":
                continue

            license_counts[license_type] += 1

            # Extract subjects
            subjects = bibjson.get("subject", [])
            for subject in subjects:
                if isinstance(subject, dict):
                    code = subject.get("code", "")
                    term = subject.get("term", "")
                    if code and term:
                        subject_counts[license_type][f"{code}|{term}"] += 1

            # Extract year from oa_start (Open Access start year)
            oa_start = bibjson.get("oa_start")
            if oa_start:
                year_counts[license_type][str(oa_start)] += 1
            else:
                year_counts[license_type]["Unknown"] += 1

            # Extract languages
            languages = bibjson.get("language", [])
            for lang in languages:
                language_counts[license_type][lang] += 1

            total_processed += 1

        page += 1
        time.sleep(RATE_LIMIT_DELAY)

    return (
        license_counts,
        subject_counts,
        language_counts,
        year_counts,
        total_processed,
    )


def save_count_data(
    license_counts, subject_counts, language_counts, year_counts
):
    """Save all collected data to CSV files."""

    # Save license counts
    with open(FILE_DOAJ_COUNT, "w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER_COUNT, dialect="unix")
        writer.writeheader()
        for lic, count in license_counts.items():
            writer.writerow({"TOOL_IDENTIFIER": lic, "COUNT": count})

    # Save subject report
    with open(
        FILE_DOAJ_SUBJECT_REPORT, "w", encoding="utf-8", newline="\n"
    ) as fh:
        writer = csv.DictWriter(
            fh, fieldnames=HEADER_SUBJECT_REPORT, dialect="unix"
        )
        writer.writeheader()
        for lic, subjects in subject_counts.items():
            for subject_info, count in subjects.items():
                if "|" in subject_info:
                    code, label = subject_info.split("|", 1)
                else:
                    code, label = subject_info, subject_info
                writer.writerow(
                    {
                        "TOOL_IDENTIFIER": lic,
                        "SUBJECT_CODE": code,
                        "SUBJECT_LABEL": label,
                        "COUNT": count,
                    }
                )

    # Save language counts with readable names
    with open(FILE_DOAJ_LANGUAGE, "w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER_LANGUAGE, dialect="unix")
        writer.writeheader()
        for lic, languages in language_counts.items():
            for lang_code, count in languages.items():
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
                writer.writerow(
                    {
                        "TOOL_IDENTIFIER": lic,
                        "LANGUAGE_CODE": lang_code,
                        "LANGUAGE": lang_name,
                        "COUNT": count,
                    }
                )

    # Save year counts
    with open(FILE_DOAJ_YEAR, "w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER_YEAR, dialect="unix")
        writer.writeheader()
        for lic, years in year_counts.items():
            for year, count in years.items():
                writer.writerow(
                    {"TOOL_IDENTIFIER": lic, "YEAR": year, "COUNT": count}
                )


def query_doaj(args):
    """Main function to query DOAJ API."""
    session = setup_session()

    # Note about articles
    LOGGER.info(
        "Note: Only processing journals - DOAJ articles don't contain "
        "license information in API"
    )

    (
        license_counts,
        subject_counts,
        language_counts,
        year_counts,
        journals_processed,
    ) = process_journals(session, args)

    # Save results
    if args.enable_save:
        save_count_data(
            license_counts, subject_counts, language_counts, year_counts
        )

    # Save provenance
    provenance_data = {
        "total_articles_fetched": 0,  # No license info in API
        "total_journals_fetched": journals_processed,
        "total_processed": journals_processed,
        "limit": args.limit,
        "quarter": QUARTER,
        "script": os.path.basename(__file__),
        "note": (
            "Articles not processed - DOAJ API doesn't provide license "
            "info for articles"
        ),
    }

    try:
        with open(FILE_PROVENANCE, "w", encoding="utf-8", newline="\n") as fh:
            yaml.dump(provenance_data, fh, default_flow_style=False, indent=2)
    except Exception as e:
        LOGGER.warning("Failed to write provenance file: %s", e)

    LOGGER.info(f"Total CC licensed journals processed: {journals_processed}")
    LOGGER.info(
        "Articles: 0 (DOAJ API doesn't provide license info for articles)"
    )


def main():
    """Main function."""
    LOGGER.info("Script execution started.")
    args = parse_arguments()
    shared.paths_log(LOGGER, PATHS)
    shared.git_fetch_and_merge(args, PATHS["repo"])
    initialize_all_data_files(args)
    query_doaj(args)
    args = shared.git_add_and_commit(
        args,
        PATHS["repo"],
        PATHS["data_quarter"],
        f"Add and commit new DOAJ CC license data for {QUARTER}",
    )
    shared.git_push_changes(args, PATHS["repo"])


if __name__ == "__main__":
    try:
        main()
    except shared.QuantifyingException as e:
        if e.exit_code == 0:
            LOGGER.info(e.message)
        else:
            LOGGER.error(e.message)
        sys.exit(e.exit_code)
    except SystemExit as e:
        if e.code != 0:
            LOGGER.error(f"System exit with code: {e.code}")
        sys.exit(e.code)
    except KeyboardInterrupt:
        LOGGER.info("(130) Halted via KeyboardInterrupt.")
        sys.exit(130)
    except Exception:
        traceback_formatted = textwrap.indent(
            highlight(
                traceback.format_exc(),
                PythonTracebackLexer(),
                TerminalFormatter(),
            ),
            "    ",
        )
        LOGGER.critical(f"(1) Unhandled exception:\n{traceback_formatted}")
        sys.exit(1)
