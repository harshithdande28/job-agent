import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SKIP_PATTERNS = [
    "linkedin", "twitter", "facebook", "instagram",
    "page=", "mailto:", "tel:", "javascript:",
    "life-at", "about", "blog", "press", "legal", "privacy"
]


def try_greenhouse_api(company_name: str) -> str | None:
    """Try Greenhouse ATS API — works for many companies."""
    slug = company_name.lower().replace(" ", "")
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            jobs = data.get("jobs", [])
            if jobs:
                return jobs[0].get("absolute_url")
    except:
        pass
    return None


def try_lever_api(company_name: str) -> str | None:
    """Try Lever ATS API — works for many startups."""
    slug = company_name.lower().replace(" ", "")
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data:
                return data[0].get("hostedUrl")
    except:
        pass
    return None


def scrape_links(url: str) -> list:
    r = requests.get(url, timeout=8, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        full_url = urljoin(url, href)
        links.append((full_url, text.lower()))
    return links


def get_one_position(career_page_url: str, company_name: str = "") -> str:
    """Try ATS APIs first, fall back to scraping."""

    # Try Greenhouse API
    if company_name:
        print("Trying Greenhouse API...")
        result = try_greenhouse_api(company_name)
        if result:
            print(f"Found via Greenhouse: {result}")
            return result

        print("Trying Lever API...")
        result = try_lever_api(company_name)
        if result:
            print(f"Found via Lever: {result}")
            return result

    # Fall back to scraping
    print("Falling back to scraping...")
    try:
        links = scrape_links(career_page_url)
        for url, text in links:
            if any(p in url.lower() for p in SKIP_PATTERNS):
                continue
            if url.rstrip("/") == career_page_url.rstrip("/"):
                continue
            parts = url.rstrip("/").split("/")
            if len(parts) >= 5:
                return url
        return "No position found"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    career_url = input("Enter career page URL: ")
    company = input("Enter company name: ")
    result = get_one_position(career_url, company)
    print(f"Position URL: {result}")