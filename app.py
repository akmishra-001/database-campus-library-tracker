import json
import sqlite3
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "library.db"
INDEX_PATH = BASE_DIR / "index.html"
HOST = "127.0.0.1"
PORT = 8000


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_dashboard_data():
    conn = get_connection()
    try:
        total_members = conn.execute("SELECT COUNT(*) AS cnt FROM members;").fetchone()["cnt"]
        total_books = conn.execute("SELECT COUNT(*) AS cnt FROM books;").fetchone()["cnt"]
        total_copies = conn.execute(
            "SELECT COALESCE(SUM(total_copies), 0) AS cnt FROM books;"
        ).fetchone()["cnt"]
        issued_count = conn.execute(
            "SELECT COUNT(*) AS cnt FROM loans WHERE status = 'Issued';"
        ).fetchone()["cnt"]
        returned_count = conn.execute(
            "SELECT COUNT(*) AS cnt FROM loans WHERE status = 'Returned';"
        ).fetchone()["cnt"]

        members = [
            dict(row)
            for row in conn.execute(
                "SELECT member_id, full_name, email, joined_date FROM members ORDER BY member_id ASC;"
            ).fetchall()
        ]

        books = [
            dict(row)
            for row in conn.execute(
                """
                SELECT
                    b.book_id,
                    b.title,
                    b.author,
                    b.category,
                    b.total_copies,
                    COALESCE(SUM(CASE WHEN l.status = 'Issued' THEN 1 ELSE 0 END), 0) AS active_issued,
                    COUNT(l.loan_id) AS total_borrows
                FROM books b
                LEFT JOIN loans l ON b.book_id = l.book_id
                GROUP BY b.book_id, b.title, b.author, b.category, b.total_copies
                ORDER BY b.book_id ASC;
                """
            ).fetchall()
        ]

        loans = [
            dict(row)
            for row in conn.execute(
                """
                SELECT
                    l.loan_id,
                    l.member_id,
                    m.full_name AS member_name,
                    l.book_id,
                    b.title AS book_title,
                    b.category,
                    l.issue_date,
                    l.return_date,
                    l.status
                FROM loans l
                JOIN members m ON l.member_id = m.member_id
                JOIN books b ON l.book_id = b.book_id
                ORDER BY CASE WHEN l.status = 'Issued' THEN 0 ELSE 1 END, l.loan_id DESC;
                """
            ).fetchall()
        ]

        return {
            "stats": {
                "total_members": total_members,
                "total_books": total_books,
                "total_copies": total_copies,
                "issued_count": issued_count,
                "returned_count": returned_count,
            },
            "members": members,
            "books": books,
            "loans": loans,
        }
    finally:
        conn.close()


def issue_book(member_id, book_id):
    conn = get_connection()
    try:
        member = conn.execute(
            "SELECT member_id FROM members WHERE member_id = ?;", (member_id,)
        ).fetchone()
        if not member:
            return 404, {"error": "Selected member not found."}

        book = conn.execute(
            """
            SELECT
                b.book_id,
                b.total_copies,
                COALESCE(SUM(CASE WHEN l.status = 'Issued' THEN 1 ELSE 0 END), 0) AS active_issued
            FROM books b
            LEFT JOIN loans l ON b.book_id = l.book_id
            WHERE b.book_id = ?
            GROUP BY b.book_id, b.total_copies;
            """,
            (book_id,),
        ).fetchone()
        if not book:
            return 404, {"error": "Selected book not found."}

        available_copies = book["total_copies"] - book["active_issued"]
        if available_copies <= 0:
            return 400, {"error": "No copies available to issue for this book."}

        today_str = date.today().isoformat()
        cur = conn.execute(
            """
            INSERT INTO loans (member_id, book_id, issue_date, return_date, status)
            VALUES (?, ?, ?, NULL, 'Issued');
            """,
            (member_id, book_id, today_str),
        )
        conn.commit()
        return 201, {"message": "Book issued successfully.", "loan_id": cur.lastrowid}
    except sqlite3.Error as exc:
        conn.rollback()
        return 500, {"error": f"Database error: {exc}"}
    finally:
        conn.close()


def return_book(loan_id):
    conn = get_connection()
    try:
        loan = conn.execute(
            "SELECT loan_id, status FROM loans WHERE loan_id = ?;", (loan_id,)
        ).fetchone()
        if not loan:
            return 404, {"error": "Loan record not found."}
        if loan["status"] == "Returned":
            return 400, {"error": "Book is already marked as Returned."}

        today_str = date.today().isoformat()
        conn.execute(
            """
            UPDATE loans
            SET return_date = ?, status = 'Returned'
            WHERE loan_id = ?;
            """,
            (today_str, loan_id),
        )
        conn.commit()
        return 200, {"message": "Book returned successfully.", "loan_id": loan_id}
    except sqlite3.Error as exc:
        conn.rollback()
        return 500, {"error": f"Database error: {exc}"}
    finally:
        conn.close()


class LibraryHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code, html_text):
        body = html_text.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            if INDEX_PATH.exists():
                self._send_html(200, INDEX_PATH.read_text(encoding="utf-8"))
            else:
                self._send_html(404, "<h1>index.html not found</h1>")
            return

        if parsed.path == "/api/dashboard":
            try:
                data = get_dashboard_data()
                self._send_json(200, data)
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            payload = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON payload."})
            return

        if parsed.path == "/api/loans/issue":
            try:
                member_id = int(payload.get("member_id"))
                book_id = int(payload.get("book_id"))
            except (TypeError, ValueError):
                self._send_json(400, {"error": "Valid member_id and book_id are required."})
                return
            status_code, res = issue_book(member_id, book_id)
            self._send_json(status_code, res)
            return

        if parsed.path == "/api/loans/return":
            try:
                loan_id = int(payload.get("loan_id"))
            except (TypeError, ValueError):
                self._send_json(400, {"error": "Valid loan_id is required."})
                return
            status_code, res = return_book(loan_id)
            self._send_json(status_code, res)
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def log_message(self, format, *args):
        return


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run schema.sql first.")
    server = ThreadingHTTPServer((HOST, PORT), LibraryHandler)
    url = f"http://{HOST}:{PORT}"
    print(f"Server running at {url} (Press Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()