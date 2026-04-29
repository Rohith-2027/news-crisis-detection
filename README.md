# News Crisis Detection System (Django + SQLite)

Local-only Django academic project that fetches Indian news from **NewsData.io**,
extracts the state mentioned, scores crisis risk from keywords, and shows the
result in a filterable dashboard.

## 1. Project structure

```
news_crisis/
├── manage.py
├── requirements.txt
├── news_crisis/         # Django project (settings, urls, wsgi)
│   ├── settings.py      # SQLite DB + NEWSDATA_API_KEY from env
│   └── urls.py
└── crisis/              # The app
    ├── models.py        # News model (title, state, risk_score, alert_level…)
    ├── utils.py         # Indian states list + crisis keywords + scoring
    ├── services.py      # fetch_and_store() — calls NewsData.io
    ├── views.py         # dashboard + /fetch-news/
    ├── urls.py
    ├── admin.py
    ├── templates/dashboard.html
    └── management/commands/fetch_news.py   # `python manage.py fetch_news`
```

## 2. Setup (local machine)

```bash
# 1) Create & activate a virtualenv
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Get a free API key from https://newsdata.io/ and export it
# Windows (PowerShell):
$env:NEWSDATA_API_KEY="your_key_here"
# macOS / Linux:
export NEWSDATA_API_KEY="your_key_here"

# 4) Apply migrations (creates db.sqlite3)
python manage.py makemigrations
python manage.py migrate

# 5) (Optional) create an admin user
python manage.py createsuperuser

# 6) Pull news the first time
python manage.py fetch_news

# 7) Run the local server
python manage.py runserver
```

Then open: **http://127.0.0.1:8000/**

- Click **🔄 Refresh / Fetch News** to call NewsData.io again.
- Use the **State** dropdown — pick "Karnataka" to see only Karnataka news,
  or "All" to see everything for India.
- Filter by **Alert Level** (LOW / MEDIUM / HIGH) and **search** by keyword.

## 3. How the crisis score works

`crisis/utils.py` defines:

```python
CRISIS_KEYWORDS = ["war", "flood", "earthquake", "riot",
                   "explosion", "attack", "cyclone", "disaster"]
```

For each news item:

```
score = total occurrences of these keywords in (title + description)
0       -> LOW   (green)
1 or 2  -> MEDIUM (yellow)
3+      -> HIGH   (red)
```

## 4. How state extraction works

`extract_state(title, description, keywords)` scans the combined text against a
predefined list of all Indian states + major UTs. First match wins. If nothing
matches, the news item is tagged **"National"**.

## 5. Constraints respected

- ✅ Django only, SQLite only, runs fully on `localhost`
- ✅ No cloud / no external DB / no deployment
- ✅ Duplicates avoided via `unique=True` on `News.title`
- ✅ Country filter defaults to India; state dropdown is dynamic
