import os
import requests
import re
import sqlite3
from dotenv import load_dotenv

# Load API credentials
load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Updated Skill dictionary for broader data roles
SKILL_CATEGORIES = {
    "Programming": ["python", "r", "scala", "java", "c++", "julia"],
    "Databases & Querying": ["sql", "postgresql", "mysql", "mongodb", "oracle"],
    "Data Visualization": ["tableau", "power bi", "looker", "excel", "qlik", "google sheets"],
    "Cloud Platforms": ["aws", "azure", "gcp"],
    "Big Data & Warehousing": ["spark", "hadoop", "snowflake", "bigquery", "redshift", "kafka"],
    "Machine Learning": ["tensorflow", "pytorch", "scikit-learn", "keras"],
    "Pipeline & DevOps": ["airflow", "dbt", "docker", "git", "kubernetes"]
}

def init_db():
    # Init SQLite 3NF
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        company TEXT,
                        location TEXT,
                        salary_min REAL,
                        salary_max REAL,
                        date_posted TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS skills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        category TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS job_skills (
                        job_id TEXT,
                        skill_id INTEGER,
                        FOREIGN KEY(job_id) REFERENCES jobs(id),
                        FOREIGN KEY(skill_id) REFERENCES skills(id),
                        UNIQUE(job_id, skill_id))''')

    # Pop skills
    for category, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            cursor.execute("INSERT OR IGNORE INTO skills (name, category) VALUES (?, ?)", (skill, category))

    conn.commit()
    conn.close()

def extract_skills(description):
    # Extract skills
    description_lower = str(description).lower()
    found_skills = []

    for category, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            if re.search(rf'\b{re.escape(skill)}\b', description_lower):
                found_skills.append(skill)
    return found_skills

def run_ingestion_pipeline(title, country, city):
    # Run ETL
    init_db()

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs')
    cursor.execute('DELETE FROM job_skills')
    conn.commit()
    total_added = 0

    print(f"\n--- DEBUG: Fetching {title} in {city}, {country} ---")

    # Fetch 10 pages
    for page in range(1, 11):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "what": title,
            "where": city,
            "results_per_page": 50
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"--- DEBUG: API error on page {page} ---")
            break

        data = response.json()
        jobs = data.get("results", [])

        if not jobs:
            break

        print(f"Page {page}: Found {len(jobs)} jobs")

        for job in jobs:
            job_id = str(job.get("id"))
            job_title = job.get("title")
            company = job.get("company", {}).get("display_name")
            location = job.get("location", {}).get("display_name")
            desc = job.get("description", "")
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            date_posted = job.get("created")

            cursor.execute('''INSERT OR IGNORE INTO jobs
                              (id, title, company, location, salary_min, salary_max, date_posted)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (job_id, job_title, company, location, salary_min, salary_max, date_posted))

            if cursor.rowcount > 0:
                total_added += 1
                skills = extract_skills(desc)
                for skill in skills:
                    cursor.execute("SELECT id FROM skills WHERE name = ?", (skill,))
                    record = cursor.fetchone()
                    if record:
                        cursor.execute("INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)",
                                       (job_id, record[0]))

    conn.commit()
    conn.close()

    print(f"--- DEBUG: Added {total_added} new jobs total ---\n")
    return {"status": "success", "jobs_added": total_added}
