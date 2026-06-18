import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

load_dotenv()

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

CAREER_PATHS = [
    "/careers", "/jobs", "/join-us", "/work-with-us",
    "/about/careers", "/company/careers", "/en/careers",
    "/en/jobs", "/careers/jobs", "/hiring", "/join"
]


def quick_find_career_page(base_url: str) -> str | None:
    """Try common career URL patterns first — fast, no LLM needed."""
    for path in CAREER_PATHS:
        url = base_url.rstrip("/") + path
        try:
            r = requests.get(url, timeout=5, headers=HEADERS)
            if r.status_code == 200:
                print(f"Found via heuristic: {url}")
                return url
        except:
            continue
    return None


def make_fetch_links_tool(base_url: str):
    @tool
    def fetch_page_links(url: str) -> str:
        """Fetches a webpage and returns all links with their anchor text."""
        try:
            if url.startswith("/"):
                parsed = urlparse(base_url)
                url = f"{parsed.scheme}://{parsed.netloc}{url}"

            r = requests.get(url, timeout=8, headers=HEADERS)
            soup = BeautifulSoup(r.text, "html.parser")

            links = []
            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True)
                href = a["href"]
                if text and len(text) < 100:
                    full_href = urljoin(url, href)
                    links.append(f'"{text}" -> {full_href}')

            return "\n".join(links[:80])
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"

    return fetch_page_links


def agent_find_career_page(company_website: str) -> str:
    """Use LLM agent to navigate to career page when heuristics fail."""
    fetch_links = make_fetch_links_tool(company_website)

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    agent = create_agent(llm, [fetch_links])

    result = agent.invoke({"messages": [
        ("user",
         f"Your goal: find the careers or jobs page URL on this company website: {company_website}\n"
         f"Instructions:\n"
         f"1. Start by fetching links from the homepage: {company_website}\n"
         f"2. Look for links with text like 'Careers', 'Jobs', 'Join Us', 'Work With Us'\n"
         f"3. If you find a careers link, return that full URL immediately\n"
         f"4. Return ONLY the full URL, nothing else")
    ]})

    return result["messages"][-1].content.strip()


def find_career_page(company_website: str) -> str:
    if not company_website:
        return "No company website provided"

    if not company_website.startswith("http"):
        company_website = "https://" + company_website

    # Use agent directly to satisfy "web agent" requirement
    print("Using web agent to find career page...")
    return agent_find_career_page(company_website)


if __name__ == "__main__":
    url = input("Enter company website URL: ")
    result = find_career_page(url)
    print(f"Career page: {result}")