# app/scraper.py

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

TARGET_URL = "https://api.freshservice.com/#ticket_attributes"

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_FILE = OUTPUT_DIR / "ticket_attributes_text.json"


def scrape_ticket_attributes_text():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(TARGET_URL, timeout=60000)
        page.wait_for_load_state("networkidle")

        # Ensure correct hash navigation
        page.evaluate("window.location.hash = '#ticket_attributes'")
        page.wait_for_timeout(2000)

        content = page.evaluate("""
        () => {
            const header = document.querySelector('#ticket_attributes');
            if (!header) return null;

            let text = header.innerText + "\\n";
            let el = header.nextElementSibling;

            while (el && !el.matches('h1, h2')) {
                text += el.innerText + "\\n";
                el = el.nextElementSibling;
            }

            return text.trim();
        }
        """)

        browser.close()
        return content


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("🔍 Scraping Freshservice ticket attributes...")
    text = scrape_ticket_attributes_text()

    if not text or len(text) < 500:
        raise RuntimeError("Scraped content is empty or too short")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": TARGET_URL,
                "content": text
            },
            f,
            indent=2
        )

    print(f" Scraping complete")
    print(f" Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
