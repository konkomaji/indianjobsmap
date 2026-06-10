#!/usr/bin/env python3
"""
Scrape NCS (National Career Service) portal for occupation descriptions.
Output: data/processed/ncs_occupations.json

NCS portal: https://ncs.gov.in
Browse by sector to get occupation listings with descriptions.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://ncs.gov.in"
OUT = Path(__file__).parent.parent / "data" / "processed" / "ncs_occupations.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (research bot — IndianJobsMap project)",
    "Accept": "text/html,application/xhtml+xml",
}

# NCS sector IDs from the portal's sector browse page
# Verify/expand these by visiting https://ncs.gov.in/Pages/BrowseByOccupation.aspx
NCS_SECTORS = [
    {"id": 1,  "name": "Agriculture"},
    {"id": 2,  "name": "Apparel"},
    {"id": 3,  "name": "Automotive"},
    {"id": 4,  "name": "Banking & Finance"},
    {"id": 5,  "name": "Beauty & Wellness"},
    {"id": 6,  "name": "Capital Goods"},
    {"id": 7,  "name": "Construction"},
    {"id": 8,  "name": "Domestic Workers"},
    {"id": 9,  "name": "Electronics"},
    {"id": 10, "name": "Food Processing"},
    {"id": 11, "name": "Gems & Jewellery"},
    {"id": 12, "name": "Healthcare"},
    {"id": 13, "name": "IT & ITeS"},
    {"id": 14, "name": "Leather"},
    {"id": 15, "name": "Logistics"},
    {"id": 16, "name": "Media & Entertainment"},
    {"id": 17, "name": "Mining"},
    {"id": 18, "name": "Plumbing"},
    {"id": 19, "name": "Retail"},
    {"id": 20, "name": "Rubber"},
    {"id": 21, "name": "Security"},
    {"id": 22, "name": "Telecom"},
    {"id": 23, "name": "Tourism & Hospitality"},
    {"id": 24, "name": "Transportation"},
]


def fetch_sector_occupations(sector_id, sector_name):
    """Fetch occupation list for a sector from NCS."""
    url = f"{BASE_URL}/Pages/BrowseByOccupation.aspx?sector={sector_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        occupations = []
        # Adjust selector to match actual NCS HTML structure
        for link in soup.select("a.occupation-link, .occupation-item a, table td a"):
            href = link.get("href", "")
            if "occupation" in href.lower() or "jobrole" in href.lower():
                occupations.append({
                    "name": link.text.strip(),
                    "url": BASE_URL + href if href.startswith("/") else href,
                    "sector": sector_name,
                })
        return occupations
    except Exception as e:
        print(f"  [WARN] sector {sector_id} ({sector_name}): {e}")
        return []


def fetch_occupation_detail(occ):
    """Fetch description, education requirement for a single occupation."""
    try:
        resp = requests.get(occ["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract description — adjust selectors to actual NCS HTML
        desc = ""
        desc_el = soup.select_one(".occupation-description, .job-description, #description")
        if desc_el:
            desc = desc_el.get_text(" ", strip=True)[:500]

        education = ""
        edu_el = soup.select_one(".education-required, .qualification, #education")
        if edu_el:
            education = edu_el.get_text(" ", strip=True)[:200]

        return {**occ, "description": desc, "education": education}
    except Exception as e:
        print(f"  [WARN] {occ['name']}: {e}")
        return {**occ, "description": "", "education": ""}


def main():
    print("Fetching NCS occupation data...")
    all_occupations = []

    for sector in NCS_SECTORS:
        print(f"  Sector: {sector['name']} (id={sector['id']})")
        occs = fetch_sector_occupations(sector["id"], sector["name"])
        print(f"    Found {len(occs)} occupations")
        all_occupations.extend(occs)
        time.sleep(1.0)  # be polite

    print(f"\nFetching details for {len(all_occupations)} occupations...")
    detailed = []
    for i, occ in enumerate(all_occupations):
        print(f"  [{i+1}/{len(all_occupations)}] {occ['name']}")
        detailed.append(fetch_occupation_detail(occ))
        time.sleep(0.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(detailed, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(detailed)} occupations → {OUT}")


if __name__ == "__main__":
    main()
