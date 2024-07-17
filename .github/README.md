# Gaming News Blog

This repository contains a Python script for scraping gaming news from various websites, generating summaries using the Gemini API, and deploying a dynamic blog using GitHub Pages.

## Getting Started

1. **Create a GitHub Repository:** Create a new GitHub repository for this project.
2. **Clone the Repository:** Clone this repository to your local machine.
3. **Replace Placeholder API Key:** Replace `"YOUR_GEMINI_API_KEY"` in `scraper.py` with your actual Gemini API key.
4. **Install Dependencies:** Run `pip install -r requirements.txt` to install the necessary Python libraries.
5. **Run the Script:** Execute `python scraper.py` to initiate the scraping and database setup.
6. **Activate GitHub Pages:** Enable GitHub Pages in your repository's settings. 
7. **Monitor:** You should see your blog automatically updated on your GitHub Pages website.

## Workflow

The provided GitHub Actions workflow will automatically:

- Run the `scraper.py` script every hour.
- Generate new HTML blog posts in the `posts` directory.
- Deploy the generated blog posts to your GitHub Pages website.

## Contributing

Feel free to contribute to this project by:

- Adding new gaming news sources.
- Improving the web scraping logic.
- Enhancing the content generation process.

## Disclaimer

This project is intended for educational purposes and may not be fully compliant with the terms of service of the websites being scraped. It is your responsibility to ensure that your usage of this code is within legal and ethical boundaries.
