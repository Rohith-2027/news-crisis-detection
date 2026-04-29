# 📰 News Crisis Detection System (India)

A Django-based web application that fetches real-time Indian news from **NewsData.io**, detects crisis-related events using keyword scoring, and displays them in a filterable dashboard.

---

## 🚀 Features

* 🔄 Fetch latest news using NewsData.io API
* 📍 State detection from news content
* 🚨 Crisis risk scoring (LOW / MEDIUM / HIGH)
* 🧠 Content-based + state-based filtering
* 🔍 Search (title + description + full content)
* ⏱️ Default view shows **recent news (last 30 minutes)**
* ♻️ Duplicate prevention (unique titles)
* 📊 Clean dashboard UI with color-coded alerts

---

## 🛠️ Tech Stack

* Backend: Django
* Database: SQLite
* Frontend: HTML, CSS
* API: NewsData.io

---

## 📂 Project Structure

```
news_crisis/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
├── crisis/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── utils.py
│   ├── urls.py
│   ├── admin.py
│   ├── templates/dashboard.html
│   └── management/commands/fetch_news.py
└── news_crisis/
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/Rohith-2027/news-crisis-detection.git
cd news-crisis-detection  

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

set NEWSDATA_API_KEY=your_api_key

python manage.py makemigrations
python manage.py migrate

python manage.py fetch_news
python manage.py runserver
```

Open:
http://127.0.0.1:8000/

---

## 🔄 Auto Fetch (Recommended)

Run this every 30 minutes:

```
python manage.py fetch_news
```

(using Windows Task Scheduler)

---

## 🧠 How It Works

1. Fetch news from NewsData.io API
2. Extract state from content
3. Compute crisis risk score
4. Store in database
5. Display:

   * Default → recent news (last 30 mins)
   * Filters/Search → full database

---

## 🚨 Crisis Scoring Logic

```python
CRISIS_KEYWORDS = ["war", "flood", "earthquake", "riot",
                   "explosion", "attack", "cyclone", "disaster"]
```

| Score | Alert     |
| ----- | --------- |
| 0     | LOW 🟢    |
| 1–2   | MEDIUM 🟡 |
| 3+    | HIGH 🔴   |

---

## 📍 State Detection

* Detects Indian states from content
* Assigns first matching state
* Defaults to **National**
* Filtering supports:

  * Exact state
  * Content-based match

---

## 📌 Highlights

* Fully local project
* No cloud / no external DB
* SQLite based
* Clean modular design

---

## 🔮 Future Improvements

* Multi-state support
* Analytics dashboard
* Real-time alerts

---

## 👨‍💻 Author

Rohith G N
