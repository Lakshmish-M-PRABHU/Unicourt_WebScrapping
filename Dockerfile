FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# INSTALL PLAYWRIGHT BROWSER BINARIES (This fixes the error!)
RUN playwright install chromium

# Copy your script
COPY playwright_scrapper.py .

CMD ["python", "playwright_scrapper.py"]
