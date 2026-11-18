# Valley State Jobs

A Progressive Web App (PWA) that aggregates active California state job postings from CalCareers across the Central Valley region into a single fast, mobile-first search interface.

## Features

- 🔍 **Search & Filter** — Find jobs by title, department, county, work type, and telework status
- 🌙 **Dark/Light Mode** — Automatic theme based on system preference, with toggle
- 📱 **PWA Ready** — Install as a native app on mobile or desktop
- 🛜 **Offline Support** — Service worker caches jobs data with network-first strategy
- ⚡ **Fast** — Minimal dependencies, optimized for GitHub Pages deployment
- 📍 **Central Valley Focus** — Covers Fresno, Madera, Kings, Tulare, and Merced counties

## Target Counties

- Fresno County
- Madera County
- Kings County
- Tulare County
- Merced County

## Project Structure

```
fresno-calcareers-pwa/
├── index.html                    # PWA frontend (self-contained HTML/CSS/JS)
├── manifest.webmanifest          # PWA manifest (standalone app config)
├── sw.js                         # Service worker (offline support)
├── data/jobs.json                # Aggregated job postings (auto-updated)
├── scraper/
│   ├── fetch_jobs.py            # Playwright scraper for CalCareers
│   └── requirements.txt          # Python dependencies
└── .github/workflows/
    └── update-jobs.yml          # Scheduled daily job updates (GitHub Actions)
```

## Setup & Deployment

### GitHub Pages

1. Enable GitHub Pages in repository settings
2. Deploy from the `main` branch (root directory)
3. The PWA will be available at `https://<user>.github.io/fresno-calcareers-pwa/`

### Local Development

```bash
# Install Python dependencies (optional for testing scraper)
pip install -r scraper/requirements.txt

# Start a local server (Python 3.11+)
python -m http.server 8000

# Visit http://localhost:8000
```

### Manual Scraper Run

```bash
python scraper/fetch_jobs.py
```

## Scraper Workflow

The GitHub Actions workflow (`update-jobs.yml`):

1. **Schedule**: Runs daily at 14:00 UTC (6:00 AM PST / 7:00 AM PDT)
2. **Manual Trigger**: Can be triggered manually via `workflow_dispatch`
3. **Process**:
   - Launches Playwright Chromium headless browser
   - Navigates to [CalCareers Advanced Job Search](https://calcareers.ca.gov/CalHRPublic/Search/AdvancedJobSearch.aspx)
   - Searches each target county
   - Extracts job details (ID, title, salary, work type, deadline, etc.)
   - Deduplicates by Job Control ID
   - Commits changes to `data/jobs.json`

## Job Data Schema

```json
{
  "last_updated": "2026-11-18T04:47:00Z",
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
      "url": "https://calcareers.ca.gov/CalHrPublic/Jobs/JobPosting.aspx?JobControlId=451234"
    }
  ]
}
```

## Service Worker Strategy

- **`./data/jobs.json`**: Network-first (fetch from server, fallback to cache)
- **Static Assets** (HTML, CSS, manifest, icons): Cache-first (use cache, fallback to network)

## Technologies

- **Frontend**: Vanilla JavaScript, CSS Grid, HTML5
- **Scraper**: Python 3.11+, Playwright (Chromium headless)
- **Deployment**: GitHub Pages + GitHub Actions
- **PWA**: Web Manifest, Service Worker, Cache API

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari 11.3+, Chrome Android)
- PWA installation support (Chrome/Edge on desktop/mobile, Firefox Android)

## Development

Minimal dependencies by design:
- No frameworks (React, Vue, etc.)
- No build step required
- No external CSS frameworks
- Self-contained CSS & JavaScript in `index.html`

## License

This project is public and available on GitHub.
