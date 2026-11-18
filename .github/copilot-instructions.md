Build a Progressive Web App (PWA) called **Valley State Jobs** (`fresno-calcareers-pwa`) that aggregates active California state job postings from CalCareers across **Fresno County and surrounding Central Valley counties** into a single fast, mobile-first search interface deployed on GitHub Pages.

### Project Architecture & Files
Create the following repository structure using relative `./` paths so everything works seamlessly under a GitHub Pages subdirectory (`https://<user>.github.io/<repo>/`):

1. `.github/workflows/update-jobs.yml` — Scheduled GitHub Actions workflow that runs daily at `14:00 UTC` (6:00 AM / 7:00 AM PST) and on manual `workflow_dispatch`, executes the Python scraper, and commits any changes to `data/jobs.json`.
2. `scraper/fetch_jobs.py` — Python script using `playwright` (Chromium headless) to query CalCareers (`https://calcareers.ca.gov/CalHRPublic/Search/AdvancedJobSearch.aspx`) for active jobs across target counties and write normalized JSON to `data/jobs.json`.
3. `scraper/requirements.txt` — Python dependencies (`playwright`).
4. `data/jobs.json` — Seeded initial JSON file with valid schema and realistic sample Fresno-area state postings so the frontend renders immediately before the first GitHub Action runs.
5. `index.html` — Self-contained HTML, CSS, and vanilla JavaScript PWA frontend.
6. `manifest.webmanifest` — PWA manifest (`display: "standalone"`, `start_url: "./index.html"`, dark theme `#0f172a`).
7. `sw.js` — Service worker using a **network-first** strategy for `./data/jobs.json` (falling back to cache when offline) and **cache-first** for static assets (`./`, `./index.html`, `./manifest.webmanifest`, `./icon-512.jpeg`).

---

### 1. Scraper Specification (`scraper/fetch_jobs.py`)
- **Target Counties (Central Valley Region):**
  - `Fresno County`
  - `Madera County`
  - `Kings County`
  - `Tulare County`
  - `Merced County`
- **Scraping Behavior:**
  - Launch Playwright Chromium headless browser.
  - Navigate to `https://calcareers.ca.gov/CalHRPublic/Search/AdvancedJobSearch.aspx`.
  - For each target county in the list:
    - Select the county in the County `<select>` element (match by option label text containing the county name), submit the search form, and wait for the results table/list to render.
    - Set results-per-page to the maximum available option if a page-size selector is present, and paginate through all result pages for that county.
    - Extract for each job posting:
      - `jc_id`: Job Control ID (e.g., `"JC-451234"`)
      - `title`: Working title / official classification title
      - `classification`: Civil service classification name
      - `department`: Hiring state agency/department
      - `county`: County name (e.g., `"Fresno County"`)
      - `salary`: Salary range string (e.g., `"$5,684.00 - $7,114.00"`)
      - `work_type`: Tenure / time base (e.g., `"Permanent - Full Time"`)
      - `telework`: Telework status if listed (`"Hybrid"`, `"Telework"`, `"In-Office"`, or `"Not Specified"`)
      - `filing_deadline`: Final filing date string (e.g., `"2026-12-05"` or `"Until Filled"`)
      - `published_date`: Posting date if available
      - `url`: Direct CalCareers posting URL (`https://calcareers.ca.gov/CalHrPublic/Jobs/JobPosting.aspx?JobControlId=<numeric_id>`)
  - Deduplicate postings by `jc_id` (if a job lists multiple counties, merge its `county` field into an array `counties: ["Fresno County", "Madera County"]`).
  - Include polite delays (`1.5`–`3` seconds between requests) and clean error handling so one failed county request does not crash the entire run.
- **Output Schema (`data/jobs.json`):**
  ```json
  {
    "last_updated": "2026-11-18T14:00:00Z",
    "total_count": 42,
    "jobs": [
      {
        "jc_id": "JC-451234",
        "title": "Information Technology Specialist I",
        "classification": "Information Technology Specialist I",
        "department": "Department of Transportation",
        "counties": ["Fresno County"],
        "salary": "$6,139.00 - $9,932.00",
        "work_type": "Permanent - Full Time",
        "telework": "Hybrid",
        "filing_deadline": "12/04/2026",
        "url": "[https://calcareers.ca.gov/CalHrPublic/Jobs/JobPosting.aspx?JobControlId=451234](https://calcareers.ca.gov/CalHrPublic/Jobs/JobPosting.aspx?JobControlId=451234)"
      }
    ]
  }
