from linkedin_api import Linkedin
from career_finder import find_career_page
from position_finder import get_one_position
from dotenv import load_dotenv
import os

load_dotenv()


def get_jobs_from_search(keywords: str, location: str, limit: int = 1) -> list:
    """Search LinkedIn and return list of company info from job listings."""
    api = Linkedin(os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD"))

    print(f"\nSearching LinkedIn for '{keywords}' in '{location}'...")
    jobs = api.search_jobs(
        keywords=keywords,
        location_name=location,
        limit=limit
    )

    results = []
    for job in jobs:
        job_id = job["entityUrn"].split(":")[-1]
        
        # Get full job details for company website
        job_details = api.get_job(job_id)
        
        COMPANY_KEY = "com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany"
        company_data = (
            job_details.get("companyDetails", {})
                       .get(COMPANY_KEY, {})
                       .get("companyResolutionResult", {})
        )

        company_name = company_data.get("name", "Unknown")
        universal_name = company_data.get("universalName", "")

        # Get company website
        company_website = None
        if universal_name:
            try:
                profile = api.get_company(universal_name)
                company_website = (
                    profile.get("companyPageUrl") or
                    profile.get("websiteUrl") or
                    profile.get("callToAction", {}).get("url")
                )
            except:
                pass

        if company_name != "Unknown" and company_website:
            results.append({
                "company_name": company_name,
                "company_website": company_website
            })
            print(f"Found: {company_name} — {company_website}")

    return results


def run_pipeline(keywords: str, location: str, limit: int = 1):
    print(f"\n{'='*60}")
    print(f"Query: '{keywords}' | Location: '{location}' | Limit: {limit}")
    print('='*60)

    # Step 1: Get companies from LinkedIn search
    print("\n[1/3] Crawling LinkedIn job listings...")
    companies = get_jobs_from_search(keywords, location, limit)

    if not companies:
        print("No companies found.")
        return

    final_results = []

    for company in companies:
        print(f"\n{'-'*40}")
        print(f"Processing: {company['company_name']}")

        # Step 2: Find career page using web agent
        print("[2/3] Web agent finding career page...")
        career_page_url = find_career_page(company["company_website"])

        # Step 3: Get one open position
        print("[3/3] Finding open position...")
        position_url = get_one_position(career_page_url, company["company_name"])

        result = {
            "company_name": company["company_name"],
            "career_page_url": career_page_url,
            "open_position_url": position_url
        }
        final_results.append(result)

    # Print final output in required format
    print(f"\n{'='*60}")
    print("FINAL RESULTS (company name, career page URL, open position URL):")
    print('='*60)
    for r in final_results:
        print(f"{r['company_name']}, {r['career_page_url']}, {r['open_position_url']}")

    return final_results


if __name__ == "__main__":
    keywords = input("Enter job search keywords (e.g. 'AI engineer'): ")
    location = input("Enter location (e.g. 'United States'): ")

    run_pipeline(keywords, location, limit=1)