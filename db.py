import sqlite3

def create_database():
    conn = sqlite3.connect('gaming_news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT UNIQUE,
                    link TEXT, 
                    content TEXT,
                    image_url TEXT, 
                    source TEXT,  # Add a column for the source
                    published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    summary TEXT)''')  # Add a column for the summary
    conn.commit()
    conn.close()

def insert_article(title, link, content, image_url, source, summary):
    conn = sqlite3.connect('gaming_news.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO articles (title, link, content, image_url, source, summary) VALUES (?, ?, ?, ?, ?, ?)",
                    (title, link, content, image_url, source, summary))
        conn.commit()
        print(f"Article '{title}' added to database.")
    except sqlite3.IntegrityError:
        print(f"Article '{title}' already exists in database.")
    conn.close()
