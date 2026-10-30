# CoachTribe Search

AI-powered search engine for the CoachTribe course library.

Built as a decoupled Python service — entirely separate from WordPress — and designed to be mounted on the CoachTribe platform via a single API endpoint.

---

## How it works

Rather than matching keywords, the search engine understands the intent behind a query. The catalogue is small, so Claude (`claude-haiku-5-5`) reads the full course list with every search and returns the courses that fit, ranked with a relevance score. The course list sits in a cached system prompt, so repeat searches only pay full price for the question. Structured outputs guarantee the answer is a list of known course IDs.

If the catalogue grows to hundreds of courses, switch to embeddings (for example Voyage AI) to pre-select candidates first.

A member searching for "hoe help ik een cliënt die vastloopt" will find the right course even if those exact words don't appear in any course title or description.

---

## Stack

- **FastAPI** — serves the search endpoint and demo UI
- **Claude** (Anthropic) — ranks the courses for each query
- **SQLite** — stores the course data
- **Python 3**

---

## Project structure

```
coachtribe-search/
├── data/
│   ├── courses.json        # Course data pulled from WordPress (not committed)
│   └── courses.db          # SQLite database the search reads (committed)
├── templates/
│   └── index.html          # Demo UI
├── fetch_courses.py        # Pulls courses from WordPress REST API
├── build_db.py             # Stores courses.json in courses.db
├── search.py               # Claude ranking
├── main.py                 # FastAPI app
├── .env                    # API keys (not committed)
└── requirements.txt        # Dependencies
```

---

## Setup

**1. Clone the repo and create a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip3 install -r requirements.txt
```

**3. Add environment variables**

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_anthropic_key
WP_USER=your_wordpress_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

**4. Fetch courses from WordPress**

```bash
python3 fetch_courses.py
```

**5. Build the course database**

```bash
python3 build_db.py
```

**6. Run the server**

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` for the demo UI or `http://localhost:8000/health` to verify the service is running.

---

## API

**POST** `/search`

Request:
```json
{
  "query": "hoe start ik een coachpraktijk",
  "top_k": 5
}
```

Response:
```json
{
  "results": [
    {
      "id": 9429,
      "title": "Het fundament onder een gezonde coachpraktijk: jouw niche",
      "description": "...",
      "url": "https://coachtribe.nl/courses/...",
      "score": 0.95
    }
  ]
}
```

---

## Limits

- Queries are 1–300 characters; `top_k` is 1–10.
- Each visitor can search 10 times per minute (429 after that). Every search is a paid Claude request.
- If Claude is unreachable the endpoint returns 503.

---

## Notes

- Three courses currently have thin or missing descriptions: *Meester In Herkaderen*, *Mindfulness*, *Vitaal Ouder Worden*. These are hard to match until descriptions are added in WordPress.
- Re-run `fetch_courses.py` and `build_db.py` when courses are added or descriptions change, then commit `data/courses.db`.
- The `.env` file and `data/courses.json` are excluded from version control.