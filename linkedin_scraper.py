from linkedin_api import Linkedin
from dotenv import load_dotenv
from urllib.parse import urlparse
import json
import os

load_dotenv()

# Wrong key (what I wrote before):
# "com.linkedin.voyager.deco.jobs.web.shared.WebJobPostingCompany"

# Correct key (from your actual response):
COMPANY_KEY = "com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany"

def get_company_info(linkedin_job_url: str) -> dict:
    parsed = urlparse(linkedin_job_url)
    job_id = parsed.path.rstrip("/").split("/")[-1]
    print(f"Extracted job ID: {job_id}")

    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        raise ValueError("LINKEDIN_EMAIL or LINKEDIN_PASSWORD not found in .env")

    api = Linkedin(email, password)
    job = api.get_job(job_id)

    # Extract company data using correct key
    company_data = (
        job.get("companyDetails", {})
           .get(COMPANY_KEY, {})
           .get("companyResolutionResult", {})
    )

    company_name = company_data.get("name", "Unknown")
    company_linkedin_url = company_data.get("url", "")
    universal_name = company_data.get("universalName", "")

    print(f"Company: {company_name}")
    print(f"Universal name: {universal_name}")

    # Get website from company profile
    company_website = None
    if universal_name:
        try:
            company_profile = api.get_company(universal_name)
            company_website = (
                company_profile.get("companyPageUrl") or
                company_profile.get("websiteUrl") or
                company_profile.get("callToAction", {}).get("url")
            )
        except Exception as e:
            print(f"Could not fetch company profile: {e}")

    return {
        "company_name": company_name,
        "company_website": company_website,
        "company_linkedin_url": company_linkedin_url
    }

if __name__ == "__main__":
    url = input("Paste a LinkedIn job URL: ")
    result = get_company_info(url)
    print(result)