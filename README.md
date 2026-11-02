# Daily Positive Quotes

A quote dashboard with a local Python backend that serves a stable quote for
each two-hour time slot, plus a scheduled GitHub Actions notification through
[ntfy](https://ntfy.sh/).

## Run locally

From this directory, start the backend:

```bash
python3 server.py
```

Then open <http://127.0.0.1:8765>. The API is available at
<http://127.0.0.1:8765/api/quote>. The same quote is returned during the
current two-hour slot, and the page refreshes automatically at the next slot.

The quote is selected deterministically from `data/quotes.json` using the
current date and slot, so refreshing the page does not change it early.
Adjacent two-hour slots are guaranteed to use different quotes. Keep at least
two quotes in the data file.

## Setup

1. Create a new GitHub repository and push this project:

   ```bash
   git init
   git add .
   git commit -m "feat: setup daily quote app"
   git branch -M main
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/daily-quotes-app.git
   git push -u origin main
   ```

2. Install the ntfy iOS app and subscribe to a long, random topic name.
   Treat the topic name like a password: anyone who knows it can publish to
   that topic.

3. In the GitHub repository, open **Settings > Secrets and variables >
   Actions**, create a repository secret named `NTFY_TOPIC`, and set it to
   the ntfy topic name.

4. Open **Settings > Pages**, choose the `main` branch and the root folder,
   then save. The site will be available at:

   `https://<YOUR-GITHUB-USERNAME>.github.io/<REPOSITORY-NAME>/`

5. To test delivery immediately, open **Actions**, select **Send Daily 8 AM
   Quote**, choose **Run workflow**, and run it manually.

GitHub Pages can host the static page but cannot run `server.py`; deploy the
backend separately if you want the API available outside your computer.

## Adding quotes

Add objects with `quote` and optional `author` fields to
[`data/quotes.json`](data/quotes.json), then commit and push the change.
The dashboard API cycles through the list using the date and two-hour slot.
The included entries are positive, first-person affirmations, and adjacent
slots are prevented from repeating the same entry.

## Schedule

The workflow runs at both 12:00 and 13:00 UTC and sends only when the runner's
time is 8:00 AM in `America/New_York`. This compensates for Eastern Time
daylight saving time, which GitHub Actions cron schedules do not understand.
