# Campus Library & Book Lending Tracker

A relational SQLite database and interactive web dashboard project developed as part of the **SQL and Database Management Systems Virtual Internship** (AICTE – EduSkills). It tracks library members, books, and book issue/return transactions while supporting SQL joins, aggregations, and real-time lending operations.

## Key Features
- **Normalized Relational Schema (3NF):** Structured `members`, `books`, and `loans` tables with `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, and `CHECK` constraints, plus performance indexes.
- **Analytical & Operational SQL Queries:** Multi-table `JOIN`s, `LEFT JOIN`s, `GROUP BY`, `HAVING`, `COUNT()`, and `SUM()` queries for active loans, member borrow frequency, popular books, and category summaries.
- **Live Web Dashboard (`app.py` + `index.html`):** Built with Python's built-in `http.server` and `sqlite3` (zero external dependencies) to view live KPI stats, issue books, and mark issued books as returned.

## Project Structure
```text
campus-library-tracker/
├── app.py          # Python backend + JSON REST endpoints + SQLite CRUD logic
├── index.html      # Interactive web UI dashboard
├── library.db      # SQLite database file
├── schema.sql      # Table definitions, constraints, indexes, and sample data
├── queries.sql     # Analytical & reporting SQL queries
├── notes.md        # Project notes, schema summary, and viva talking points
└── README.md       # Project documentation




Start the backend server and open the dashboard (http://127.0.0.1:8000):

python app.py

Author: 
Abhishek Mishra (MCA, Invertis University)