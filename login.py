
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs
from html import escape
from decimal import Decimal
import mssql_python

# Folder where this Python file is saved
FOLDER = Path(__file__).resolve().parent


def get_grade(per):
    if per >= 90:
        return "A+"
    elif per >= 75:
        return "A"
    elif per >= 60:
        return "B"
    elif per >= 45:
        return "C"
    else:
        return "F"


class StudentHandler(BaseHTTPRequestHandler):

    def send_page(self, page, status=200):
        data = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != "/":
            self.send_page("<h2>Page not found</h2>", 404)
            return

        try:
            html_file = FOLDER / "index.html"
            page = html_file.read_text(encoding="utf-8")
            self.send_page(page)
        except FileNotFoundError:
            self.send_page(
                "<h2>index.html not found</h2>"
                "<p>Save index.html in the same folder as login.py.</p>",
                404
            )

    def do_POST(self):
        if self.path != "/register":
            self.send_page("<h2>Page not found</h2>", 404)
            return

        conn = None

        try:
            length = int(self.headers.get("Content-Length", 0))

            if length <= 0 or length > 10000:
                raise ValueError("Invalid form data.")

            body = self.rfile.read(length).decode("utf-8")
            form = parse_qs(body, strict_parsing=True)

            name = form["name"][0].strip()
            age = int(form["age"][0])
            per = Decimal(form["percentage"][0])
            stream = form["stream"][0]

            # Validate data on the server
            if len(name) < 2 or len(name) > 100:
                raise ValueError("Name must contain 2 to 100 characters.")

            if not 5 <= age <= 100:
                raise ValueError("Age must be between 5 and 100.")

            if not per.is_finite() or not 0 <= per <= 100:
                raise ValueError("Percentage must be between 0 and 100.")

            if stream not in ("Science", "Commerce", "Arts"):
                raise ValueError("Please select a valid stream.")

            grade = get_grade(per)

            # Connect to SQL Server
            conn = mssql_python.connect(
                "Server=ASUS;"
                "Database=StudentDB;"
                "Trusted_Connection=yes;"
                "Encrypt=no;"
            )

            cursor = conn.cursor()

            # Save student information
            cursor.execute(
                """
                INSERT INTO dbo.Students
                    (Name, Age, Percentage, Stream, Grade)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, age, float(per), stream, grade)
            )

            conn.commit()

            # Display confirmation
            page = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Registration Successful</title>
            </head>
            <body>
                <h2>Registration Successful!</h2>
                <p>Name: {escape(name)}</p>
                <p>Age: {age}</p>
                <p>Percentage: {per}%</p>
                <p>Stream: {escape(stream)}</p>
                <p>Grade: {grade}</p>
                <h3>Student saved in SQL Server!</h3>
                <a href="/">Register another student</a>
            </body>
            </html>
            """

            self.send_page(page)

        except (ValueError, KeyError, ArithmeticError,
                UnicodeError):
            self.send_page(
                '<h2>Invalid details.</h2>'
                '<a href="/">Go back</a>',
                400
            )

        except Exception as error:
            print("Database error:", repr(error))
            self.send_page(
                '<h2>Could not save student.</h2>'
                '<p>Check the IDLE Shell for the error.</p>'
                '<a href="/">Go back</a>',
                500
            )

        finally:
            if conn is not None:
                conn.close()


server = HTTPServer(("127.0.0.1", 8000), StudentHandler)

print("Student Registration Server Started")
print("Open http://127.0.0.1:8000 in Chrome")
print("Press Ctrl+C to stop the server")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Server stopped.")
finally:
    server.server_close()
