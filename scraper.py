import requests
from bs4 import BeautifulSoup
import os
import sqlite3
from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
import time

# --- Gemini API Integration ---
GEMINI_API_KEY = ""  # Replace with your actual API key
GEMINI_API_URL = "https://generativeai.googleapis.com/v1beta/models/text-bison:generateText"

def summarize_with_gemini(text):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": f"Summarize this text in 200 words or less:\n{text}",
        "temperature": 0.7,  # Adjust for different levels of summarization creativity
        "maxOutputTokens": 400  # Adjust the maximum length of the summary
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=data)
    response.raise_for_status()

    response_data = response.json()
    summary = response_data['text']  # Extract the summary from the response

    return summary

# --- Database Setup (SQLite for demonstration) ---
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

# --- Function to Fetch and Save Featured Images ---
def fetch_and_save_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        os.makedirs("images", exist_ok=True)  # Create the 'images' folder if it doesn't exist

        with open(f"images/{filename}", "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"Image downloaded successfully: {filename}")
    except Exception as e:
        print(f"Error downloading image: {e}")

# --- Web Scraping and Processing ---
def scrape_and_save_articles(target_urls):
    create_database()

    for target_url in target_urls:
        try:
            response = requests.get(target_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('div', class_='c-entry-box--compact__body')  # Adjust selector if needed

            for article in articles:
                title = article.find('h2').text.strip()
                link = article.find('a')['href']
                content_element = article.find('p')
                content = content_element.text.strip() if content_element else "Content not found"
                # --- Fetch Image ---
                image_element = article.find('img', class_='c-entry-box--compact__image')  # Adjust selector if needed
                image_url = image_element['src'] if image_element else None

                # --- Download and Save the Image ---
                if image_url:
                    image_filename = f"{title.replace(' ', '_').lower()}.jpg"
                    fetch_and_save_image(image_url, image_filename)

                # --- Store in Database (including source) ---
                conn = sqlite3.connect('gaming_news.db')
                c = conn.cursor()
                try:
                    # Determine the source based on the target_url
                    if 'polygon.com' in target_url:
                        source = 'Polygon'
                    elif 'gameinformer.com' in target_url:
                        source = 'Game Informer'
                    elif 'ign.com' in target_url:
                        source = 'IGN'
                    elif 'gamespot.com' in target_url:
                        source = 'GameSpot'
                    elif 'gamerant.com' in target_url:
                        source = 'Game Rant'
                    elif 'n4g.com' in target_url:
                        source = 'N4G'
                    else:
                        source = 'Unknown'

                    # --- Generate Summary with Gemini API ---
                    summary = summarize_with_gemini(content)

                    c.execute("INSERT INTO articles (title, link, content, image_url, source, summary) VALUES (?, ?, ?, ?, ?, ?)",
                                (title, link, content, image_url, source, summary))
                    conn.commit()
                    print(f"Article '{title}' added to database.")
                except sqlite3.IntegrityError:
                    print(f"Article '{title}' already exists in database.")
                conn.close()

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {target_url}: {e}")

# --- Generate HTML (You can adapt this part to use Flask/Django templates) ---
def generate_homepage():
    conn = sqlite3.connect('gaming_news.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles ORDER BY published_date DESC")
    articles = c.fetchall()
    conn.close()

    post_html = ""
    for article in articles:
        title, link, content, image_url, source, published_date, summary = article
        post_html += f"""
            <div class="article">
                <h2><a href="{link}">{title}</a></h2>
                {f'<img src="images/{image_url.split('/')[-1]}" alt="{title}">' if image_url else ''}
                <p>{summary}</p> 
                <p class="date">Published: {published_date}</p>
                <p>Source: {source}</p>
            </div>
        """

    with open("posts/index.html", "w", encoding="utf-8") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ctrl+Play: Your Daily Dose of Gaming</title>
            <link rel="stylesheet" href="style.css"> 
        </head>
        <body>
            <h1>Ctrl+Play: Your Daily Dose of Gaming</h1>
            {post_html}
        </body>
        </html>
        """)

# --- Scheduler Setup ---
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_and_save_articles, 'interval', hours=1, args=[target_urls])
    scheduler.add_job(generate_homepage, 'interval', hours=1)  # Schedule HTML generation
    scheduler.start()

    try:
        # Keep the main thread alive (for the scheduler to run)
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

# --- Example Usage ---
target_urls = [
    'https://www.polygon.com/games',
    'https://www.gameinformer.com/',
    'https://www.ign.com/',
    'https://www.gamespot.com/',
    'https://gamerant.com/',
    'https://n4g.com/'
]

# --- Start the scheduler ---
if __name__ == "__main__":
    start_scheduler()
