import os
from flask import Flask, render_template, request, jsonify
import sqlite3
from fetch_jobs import run_ingestion_pipeline, init_db

app = Flask(__name__)

@app.route("/")
def index():
    if os.path.exists("jobs.db"):
        os.remove("jobs.db")

    init_db()
    return render_template("index.html")

@app.route("/api/sync-data", methods=["POST"])
def sync_data():
    data = request.get_json() or {}
    country = data.get("country")
    city = data.get("city", "")
    target = data.get("target")

    result = run_ingestion_pipeline(title=target, country=country, city=city)
    return jsonify(result)

@app.route("/api/top-skills")
def top_skills():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT s.name, s.category, COUNT(js.job_id) AS demand_count
        FROM skills s
        LEFT JOIN job_skills js ON s.id = js.skill_id
        GROUP BY s.id
        HAVING demand_count > 0
        ORDER BY demand_count DESC
        LIMIT 15
    ''')

    results = [{"name": row[0], "category": row[1], "count": row[2]} for row in cursor.fetchall()]
    conn.close()

    return jsonify(results)

@app.route("/api/insights")
def get_insights():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(id) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    if total_jobs == 0:
        return jsonify({"insights": ["No data available yet. Please run a search to generate insights!"]})

    insights = [f"Analyzed a total of <strong>{total_jobs}</strong> recent job postings."]

    # Helper function to ensure SQL is always fully capitalized
    def format_skill(skill_name):
        if skill_name.lower() == 'sql':
            return 'SQL'
        return skill_name.title()

    # Top overall skills
    cursor.execute('''
        SELECT s.name, COUNT(js.job_id) as demand_count
        FROM skills s
        JOIN job_skills js ON s.id = js.skill_id
        GROUP BY s.id
        ORDER BY demand_count DESC
        LIMIT 2
    ''')
    top_skills = cursor.fetchall()

    if len(top_skills) > 0:
        top_skill = top_skills[0]
        percentage = round((top_skill[1] / total_jobs) * 100)
        insights.append(f"The most requested skill is <strong>{format_skill(top_skill[0])}</strong>, appearing in <strong>{percentage}%</strong> of all postings.")

    if len(top_skills) > 1:
        second_skill = top_skills[1]
        if second_skill[1] > 0:
            ratio = round(top_skill[1] / second_skill[1], 1)
            if ratio > 1.0:
                insights.append(f"<strong>{format_skill(top_skill[0])}</strong> outranks <strong>{format_skill(second_skill[0])}</strong> by <strong>{ratio}x</strong> in this specific market.")

    # Dominant Category
    cursor.execute('''
        SELECT s.category, COUNT(js.job_id) as demand_count
        FROM skills s
        JOIN job_skills js ON s.id = js.skill_id
        GROUP BY s.category
        ORDER BY demand_count DESC
        LIMIT 1
    ''')
    top_cat = cursor.fetchone()
    if top_cat:
        insights.append(f"The dominant skill category is <strong>{top_cat[0]}</strong> with {top_cat[1]} total mentions.")

    conn.close()
    return jsonify({"insights": insights})

if __name__ == "__main__":
    app.run(debug=True)
