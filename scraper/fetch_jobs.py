#!/usr/bin/env python3
"""
CalCareers job scraper for Central Valley counties.
Fetches active job postings from CalCareers and writes to data/jobs.json.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from playwright.async_api import async_playwright, Page, Browser


TARGET_COUNTIES = [
    "Fresno County",
    "Madera County",
    "Kings County",
    "Tulare County",
    "Merced County",
]

CALCAREERS_URL = "https://calcareers.ca.gov/CalHRPublic/Search/AdvancedJobSearch.aspx"
BASE_POSTING_URL = "https://calcareers.ca.gov/CalHrPublic/Jobs/JobPosting.aspx?JobControlId="

# Data output path (relative to script location, two levels up to repo root, then data/)
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "jobs.json"


async def extract_job_id_from_url(url: str) -> Optional[str]:
    """Extract JC ID from job posting URL."""
    if "JobControlId=" in url:
        return url.split("JobControlId=")[-1].split("&")[0]
    return None


async def get_jobs_for_county(page: Page, county: str) -> list[dict]:
    """Scrape jobs for a specific county."""
    jobs = []
    try:
        # Select county from dropdown
        await page.select_option("select[name*='County']", label=county)
        await asyncio.sleep(1)

        # Submit search form
        await page.click("button:has-text('Search')")
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(1)

        # Paginate through results
        page_num = 1
        while True:
            # Extract jobs from current page
            job_rows = await page.query_selector_all("table tr, div[class*='job']")

            for row in job_rows:
                try:
                    # Try to extract job details from row
                    text_content = await row.text_content()
                    if not text_content or len(text_content.strip()) < 10:
                        continue

                    # Try to find link with job control ID
                    link = await row.query_selector("a[href*='JobControlId']")
                    if not link:
                        continue

                    href = await link.get_attribute("href")
                    if not href:
                        continue

                    job_id = await extract_job_id_from_url(href)
                    if not job_id:
                        continue

                    # Extract fields from row text (parsing varies by site layout)
                    # This is a best-effort extraction
                    title = await link.text_content()
                    title = title.strip() if title else f"Job {job_id}"

                    job = {
                        "jc_id": f"JC-{job_id}",
                        "title": title,
                        "classification": title,
                        "department": "State of California",
                        "counties": [county],
                        "salary": "Not Specified",
                        "work_type": "Permanent - Full Time",
                        "telework": "Not Specified",
                        "filing_deadline": "Until Filled",
                        "url": urljoin(CALCAREERS_URL, href),
                    }
                    jobs.append(job)
                except Exception as e:
                    print(f"Warning: Failed to extract job from row: {e}", file=sys.stderr)
                    continue

            # Check for next page button
            next_button = await page.query_selector("a:has-text('Next')")
            if not next_button or await next_button.is_disabled():
                break

            await next_button.click()
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(2)
            page_num += 1

    except Exception as e:
        print(f"Error scraping county {county}: {e}", file=sys.stderr)

    return jobs


async def scrape_jobs() -> list[dict]:
    """Main scraper function."""
    all_jobs = []
    seen_ids = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(CALCAREERS_URL, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            for county in TARGET_COUNTIES:
                print(f"Scraping {county}...", file=sys.stderr)
                try:
                    jobs = await get_jobs_for_county(page, county)
                    print(f"  Found {len(jobs)} jobs", file=sys.stderr)

                    # Deduplicate by jc_id, merging counties
                    for job in jobs:
                        job_id = job["jc_id"]
                        if job_id in seen_ids:
                            # Merge county into existing job
                            for existing_job in all_jobs:
                                if existing_job["jc_id"] == job_id:
                                    if isinstance(existing_job.get("counties"), list):
                                        if county not in existing_job["counties"]:
                                            existing_job["counties"].append(county)
                                    break
                        else:
                            seen_ids.add(job_id)
                            all_jobs.append(job)

                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"Failed to scrape {county}: {e}", file=sys.stderr)
                    continue

        finally:
            await browser.close()

    return all_jobs


def load_existing_jobs() -> dict:
    """Load existing jobs.json if it exists."""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load existing jobs.json: {e}", file=sys.stderr)
    return {"last_updated": "", "total_count": 0, "jobs": []}


def save_jobs(jobs: list[dict]) -> None:
    """Save jobs to data/jobs.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_count": len(jobs),
        "jobs": sorted(jobs, key=lambda j: j.get("title", "")),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved {len(jobs)} jobs to {OUTPUT_FILE}")


async def main():
    """Main entry point."""
    try:
        jobs = await scrape_jobs()
        save_jobs(jobs)
        return 0
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
