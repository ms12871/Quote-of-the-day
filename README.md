# Daily Positive Quotes

Daily Positive Quotes is a mobile-friendly affirmation app that displays
encouraging, first-person quotes throughout the day. A lightweight Python
backend selects one affirmation for each two-hour time slot, while the
frontend updates automatically when the next slot begins.

## Live website

**Open the app:** <https://ms12871.github.io/Quote-of-the-day/>

The website is designed for phones, tablets, and desktop browsers. It uses a
calm, responsive card layout and shows the current affirmation, author label,
and the next scheduled update time.

## Features

- Positive, first-person daily affirmations.
- A new quote every two hours.
- Stable results within each two-hour slot.
- Adjacent slots never repeat the same quote.
- Automatic refresh at the next two-hour boundary.
- Mobile-first layout with iPhone safe-area support.
- No frontend frameworks or external runtime dependencies.
- Optional ntfy push notifications through GitHub Actions.

## Run locally

From the project directory:

```bash
python3 server.py
```

Then open:

<http://127.0.0.1:8765>

The quote API is available at:

<http://127.0.0.1:8765/api/quote>

Press `Ctrl+C` in the terminal to stop the server.

## How quote rotation works

Quotes are stored in [`data/quotes.json`](data/quotes.json). The backend uses
the current date and two-hour time slot to select an affirmation
deterministically:

- Refreshing the page during the same slot keeps the same quote.
- The quote changes at 12:00 AM, 2:00 AM, 4:00 AM, and every two hours after.
- The next slot is prevented from repeating the previous slot's quote.
- At least two quotes must be present in `data/quotes.json`.

## Project structure

```text
.
├── .github/
│   └── workflows/
│       └── daily-quote.yml   # Scheduled ntfy notification workflow
├── data/
│   └── quotes.json           # Affirmation library
├── index.html                # Responsive web interface
└── server.py                 # Local API and web server
```

## Add or edit affirmations

Add entries to [`data/quotes.json`](data/quotes.json) using this format:

```json
{
  "quote": "I trust myself to take the next positive step.",
  "author": "Daily Affirmation"
}
```

Keep the wording positive and affirmative. Commit and push the file to update
the quote library used by the app.

## Optional iPhone notifications

The repository includes a GitHub Actions workflow that can send a morning
affirmation through [ntfy](https://ntfy.sh/).

1. Install the ntfy app on your iPhone.
2. Subscribe to a long, random topic name. Treat it like a password.
3. In GitHub, open **Settings > Secrets and variables > Actions**.
4. Create a repository secret named `NTFY_TOPIC` with your topic name.
5. Open **Actions**, select **Send Daily 8 AM Quote**, and choose **Run
   workflow** to test it.

The scheduled workflow runs around 8:00 AM Eastern Time. It checks both
possible UTC times so it continues to work during daylight-saving time.

## Deployment note

GitHub Pages hosts the static frontend at the live website link above. GitHub
Pages cannot run the Python backend, so the two-hour API behavior requires
running `server.py` locally or deploying the backend to a Python-compatible
hosting service.
