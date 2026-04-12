from flask import Flask, jsonify, render_template, request
import sqlite3
import os
from datetime import date

app = Flask(__name__)

app.config["DATABASE"] = "db/books.db"


def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
    return conn
    
@app.route('/api/books', methods=['GET'])
def get_all_books():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Books")
        books = cursor.fetchall()
        conn.close()

        book_list = []
        for book in books:
            book_dict = {
                'book_id': book[0],
                'title': book[1],
                'publication_year': book[2],
                'book_author': book[3],
                'url': book[4]
            }
            book_list.append(book_dict)

        return jsonify({'books': book_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_books():
    try:
        query = request.args.get('q', '').strip()

        if not query:
            return jsonify({'books': []})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Books
            WHERE LOWER(title) LIKE ?
               OR LOWER(book_author) LIKE ?
        """, (f"%{query.lower()}%", f"%{query.lower()}%"))

        books = cursor.fetchall()
        conn.close()

        book_list = []
        for book in books:
            book_dict = {
                'book_id': book[0],
                'title': book[1],
                'publication_year': book[2],
                'book_author': book[3],
                'url': book[4]
            }
            book_list.append(book_dict)

        return jsonify({'books': book_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_db():
    os.makedirs("db", exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Reviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER,
        review_text TEXT,
        review_date DATE
    )
""")

    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM Reviews")
    count = cursor.fetchone()[0]

    if count == 0:
        print("Seeding initial reviews...")

        seed_reviews = [
            # Harry Potter
            ("Harry Potter", "Alice", 5, "Amazing world-building and characters!", "2026-04-12"),
            ("Harry Potter", "Jimmy", 4, "Loved it, but a bit slow at times.", "2026-04-12"),
            
            # Maze Runner
            ("Maze Runner", "Charlie", 4, "Very suspenseful and intense.", "2026-04-12"),
            ("Maze Runner", "Dana", 3, "Interesting concept but confusing at times.", "2026-04-12"),
            
            # Percy Jackson
            ("Percy Jackson", "Eve", 5, "Super fun and creative mythology twist!", "2026-04-12"),
            ("Percy Jackson", "Frank", 4, "Great for younger audiences, still enjoyable.", "2026-04-12")
        ]

        cursor.executemany("""INSERT INTO Reviews (book_id, user_id, rating, review_text, review_date) VALUES (?, ?, ?, ?, ?) """, seed_reviews)

    conn.commit()
    conn.close()


@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""SELECT review_id, book_id, user_id, rating, review_text, review_date FROM Reviews""") 
        rows = cursor.fetchall()
        conn.close()

        reviews = []
        for row in rows:
            reviews.append({
                'book_id': row[1],
                'user': row[2],
                'rating': row[3],
                'comment': row[4]
            })

        return jsonify({'reviews': reviews})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add_review', methods=['POST'])
def add_review():
    try:
        data = request.get_json()

        book_id = data.get('book_id')
        user = data.get('user')
        rating = data.get('rating')
        comment = data.get('comment')

        if not book_id or not user or rating is None:
            return jsonify({'error': 'book_id, user, and rating are required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
    INSERT INTO Reviews (book_id, user_id, rating, review_text, review_date)
    VALUES (?, ?, ?, ?, ?)
""", (book_id, user, rating, comment, date.today().isoformat()))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Review added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/authors', methods=['GET'])
def get_all_authors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Authors")
        authors = cursor.fetchall()
        conn.close()
        return jsonify(authors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add', methods=['POST'])
def add_book():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        data = request.get_json()
        title = data.get('title')
        publication_year = data.get('publication_year')
        book_author = data.get('author')
        url = data.get('url')

        cursor.execute(
            "INSERT INTO Books (title, publication_year, book_author, url) VALUES (?, ?, ?, ?)",
            (title, publication_year, book_author, url)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Book added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')


init_db()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
