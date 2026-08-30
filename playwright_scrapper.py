import asyncio  # <-- Make sure this line is here!
import os
from playwright.async_api import async_playwright
import psycopg2

async def scrape_and_save():
  # 1. Scrape all target content using Playwright
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()

    # We can scrape the writing-tests page which contains the tables and info you wanted
    await page.goto("https://playwright.dev/docs/writing-tests")

    # Extract Introduction/Main paragraph
    intro_locator = page.locator("article p").first
    intro_text = await intro_locator.inner_text()

    # Extract all tables (Actions and Assertions)
    tables = page.locator("article table")
    table_count = await tables.count()

    scraped_rows = []
    for i in range(table_count):
      table_type = "Action" if i == 0 else "Assertion"
      rows = tables.nth(i).locator("tr")
      row_count = await rows.count()

      for j in range(row_count):
        cells = rows.nth(j).locator("td")
        if await cells.count() >= 2:
          name = await cells.nth(0).inner_text()
          description = await cells.nth(1).inner_text()
          #scraped_rows.import_data = (table_type, name, description)
          scraped_rows.append((table_type, name.strip(), description.strip()))

    await browser.close()

  # 2. Connect to the PostgreSQL container
  conn = psycopg2.connect(
      dbname=os.getenv("DB_NAME", "scraper_db"),
      user=os.getenv("DB_USER", "postgres"),
      password=os.getenv("DB_PASSWORD", "secretpassword"),
      host=os.getenv("DB_HOST", "db"),
      port=os.getenv("DB_PORT", "5432"),
  )
  cursor = conn.cursor()

  # 3. Create tables for structured storage
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS playwright_docs (
            id SERIAL PRIMARY KEY,
            category VARCHAR(50),
            name TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

  # 4. Insert all extracted table rows into PostgreSQL
  for category, name, description in scraped_rows:
    cursor.execute(
        """
            INSERT INTO playwright_docs (category, name, description) 
            VALUES (%s, %s, %s);
        """,
        (category, name, description),
    )

  conn.commit()
  cursor.close()
  conn.close()

  print(
      f"--- Successfully saved {len(scraped_rows)} items (Actions &"
      " Assertions) to PostgreSQL! ---"
  )


if __name__ == "__main__":
  asyncio.run(scrape_and_save())
