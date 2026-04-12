from flask import Flask, jsonify, render_template, request
import sqlite3
import os

app = Flask(__name__)

app.config["DATABASE"] = "db/books.db"


def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
    return conn


def init_db():
    os.makedirs("db", exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            user TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT
        )
    """)

    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM Reviews")
    count = cursor.fetchone()[0]

    if count == 0:
        print("Seeding initial reviews...")

        seed_reviews = [
            # Harry Potter
            ("1", "Alice", 5, "Amazing world-building and characters!"),
            ("1", "Bob", 4, "Loved it, but a bit slow at times."),
            
            # Maze Runner
            ("2", "Charlie", 4, "Very suspenseful and intense."),
            ("2", "Dana", 3, "Interesting concept but confusing at times."),
            
            # Percy Jackson
            ("3", "Eve", 5, "Super fun and creative mythology twist!"),
            ("3", "Frank", 4, "Great for younger audiences, still enjoyable.")
        ]

        cursor.executemany("""
            INSERT INTO Reviews (book_id, user, rating, comment)
            VALUES (?, ?, ?, ?)
        """, seed_reviews)

    conn.commit()
    conn.close()


@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT book_id, user, rating, comment FROM Reviews")
        rows = cursor.fetchall()
        conn.close()

        reviews = []
        for row in rows:
            reviews.append({
                'book_id': row[0],
                'user': row[1],
                'rating': row[2],
                'comment': row[3]
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
            INSERT INTO Reviews (book_id, user, rating, comment)
            VALUES (?, ?, ?, ?)
        """, (book_id, user, rating, comment))

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
