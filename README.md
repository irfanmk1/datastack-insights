# DataStack Insights

#### Description:
**DataStack Insights** is an interactive web dashboard that helps you see what data skills companies are actually hiring for in real time. Built as my CS50 final project, the app connects to the live Adzuna Job Search API, pulls in hundreds of job postings for specific roles and cities, and scans the descriptions for essential technical skills. It then stores everything in a clean SQLite database and turns the raw numbers into interactive charts and clear takeaways—so instead of guessing which tool to learn next, you have actual market data to back it up.

---

### Project File Structure

The project follows a standard, modular structure tailored for Flask applications:

*   **`app.py`**: The core Flask application server. It defines the routing logic, coordinates API requests, and serves JSON endpoints for chart rendering and analytical insights.
*   **`fetch_jobs.py`**: The ETL (Extract, Transform, Load) pipeline. It connects to the Adzuna API, paginates through search results based on user filters, resets previous search records in the database, extracts relevant skill keywords using Regular Expressions (`re`), and writes structured data into the database.
*   **`templates/index.html`**: The frontend view. Built with Tailwind CSS and Google Fonts (Inter), it provides a responsive, modern SaaS layout featuring search controls, side-by-side Chart.js visualizations, and an automated insights card.
*   **`static/js/script.js`**: Handles client-side interactivity, including dynamic cascading dropdowns (populating cities based on selected countries), asynchronous API calls (`fetch`), status loading spinners, and the configuration and rendering of Chart.js bar and doughnut charts.
*   **`static/css/style.css`**: Custom CSS styling providing smooth UI transitions, custom scrollbars, and precise sizing boxes for responsive chart containers.
*   **`requirements.txt`**: Lists all required Python packages (`Flask`, `requests`, `python-dotenv`).

---

### Technical Implementation Details

#### 1. Backend & Routing (`app.py`)
Flask serves as the lightweight backend framework. It routes client requests, manages API endpoints, and coordinates with the ingestion pipeline to serve clean, up-to-date data directly to the frontend interface.

#### 2. The ETL Pipeline (`fetch_jobs.py`)
*   **Extract**: The pipeline interfaces with the Adzuna Job Search API, querying listings across 20+ supported countries and filtering by specific job titles and cities. It iterates through multiple pages (up to 500 listings per search) to gather a statistically meaningful sample.
*   **Transform**: Job descriptions are converted to lowercase and scanned using precise regular expression boundary matching (`\b`) to detect technical skills without catching false positives (e.g., ensuring "R" as a standalone programming language isn't triggered by words containing the letter r).
*   **Load**: Data is structured into a normalized 3rd Normal Form (3NF) SQLite database with three primary tables: `jobs` (storing unique job metadata via Adzuna IDs), `skills` (storing reference skill names and categories), and `job_skills` (a junction table mapping jobs to required skills). Before ingesting fresh data, the pipeline automatically clears previous search records from the database, ensuring metrics never mix across different queries.

#### 3. Modern Data Taxonomy
The application categorizes technical competencies into 7 distinct pillars representing the modern data stack:
1.  **Programming**: Python, R, Scala, Java, C++, Julia.
2.  **Databases & Querying**: SQL, PostgreSQL, MySQL, MongoDB, Oracle.
3.  **Data Visualization**: Tableau, Power BI, Looker, Excel, Qlik, Google Sheets.
4.  **Cloud Platforms**: AWS, Azure, GCP.
5.  **Big Data & Warehousing**: Spark, Hadoop, Snowflake, BigQuery, Redshift, Kafka.
6.  **Machine Learning**: TensorFlow, PyTorch, Scikit-learn, Keras.
7.  **Pipeline & DevOps**: Airflow, dbt, Docker, Git, Kubernetes.

#### 4. Frontend Design & Visualizations
The user interface adopts a professional slate-and-indigo color palette inspired by modern enterprise SaaS applications.
*   **Top Skills Demand (Bar Chart)**: A horizontal bar chart displaying the 15 most requested individual skills, styled with a vertical linear gradient and optimized Y-axis tracking tooltips.
*   **Skill Category Breakdown (Doughnut Chart)**: A proportional breakdown illustrating which major sector of the data stack dominates the selected job market.
*   **Insights & Takeaways**: A dynamic analytics engine that computes key business takeaways on the fly—such as calculating exact percentage penetrations and comparative skill ratios.

---

### How to Run the Project

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/irfanmk1/datastack-insights.git](https://github.com/irfanmk1/datastack-insights.git)
    cd datastack-insights
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Credentials**:
    Create a `.env` file in the root directory and add your Adzuna API keys:
    ```env
    ADZUNA_APP_ID=your_actual_app_id
    ADZUNA_APP_KEY=your_actual_app_key
    ```
    *(Note: Free API credentials can be obtained by registering at [Adzuna Developer Portal](https://developer.adzuna.com/))*

4.  **Run the Application**:
    ```python
    python app.py
    ```

5.  **Access the Dashboard**:
    Open your web browser and navigate to `http://127.0.0.1:5000`. Select your desired country, city, and target data role, then click **Search Jobs** to populate live insights!

---

### Acknowledgments
This project was built as the final submission for **CS50's Introduction to Computer Science**. Special thanks to the teaching staff for providing a foundational understanding of C, Python, SQL, Flask, and web development principles.
