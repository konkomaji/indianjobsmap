#!/usr/bin/env python3
"""
Merge PLFS statistics with NCS occupation descriptions.
Input:  data/processed/plfs_by_nco.json
        data/processed/ncs_occupations.json  (optional)
Output: data/processed/occupations_base.json
"""

import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed"
OUT = DATA / "occupations_base.json"


def build_ncs_lookup(ncs_path):
    """Build name→description lookup from NCS data."""
    if not ncs_path.exists():
        print("NCS data not found — run 1_fetch_ncs.py first (optional)")
        return {}

    ncs = json.loads(ncs_path.read_text())
    lookup = {}
    for occ in ncs:
        name_key = occ.get("name", "").lower().strip()
        lookup[name_key] = {
            "description": occ.get("description", ""),
            "education": occ.get("education", ""),
            "ncs_url": occ.get("url", "https://ncs.gov.in"),
        }
    return lookup


def match_ncs(occ_name, ncs_lookup):
    """Fuzzy match occupation name to NCS data."""
    name_lower = occ_name.lower()

    # Exact match
    if name_lower in ncs_lookup:
        return ncs_lookup[name_lower]

    # Partial match: check if any NCS name is contained in or contains occ name
    for key, val in ncs_lookup.items():
        if key in name_lower or name_lower in key:
            return val

    return {"description": "", "education": "", "ncs_url": "https://ncs.gov.in"}


def main():
    plfs_path = DATA / "plfs_by_nco.json"
    ncs_path = DATA / "ncs_occupations.json"

    if not plfs_path.exists():
        print(f"PLFS data not found: {plfs_path}")
        print("Run 2_parse_plfs.py first.")
        return

    plfs_data = json.loads(plfs_path.read_text())
    ncs_lookup = build_ncs_lookup(ncs_path)

    print(f"PLFS occupations: {len(plfs_data)}")
    print(f"NCS descriptions: {len(ncs_lookup)}")

    merged = []
    for occ in plfs_data:
        ncs = match_ncs(occ["name"], ncs_lookup)
        merged.append({
            **occ,
            "description": ncs["description"],
            "education": ncs["education"],
            "ncs_url": ncs["ncs_url"],
        })

    # Sort by employment descending
    merged.sort(key=lambda x: -x["employment"])

    OUT.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    print(f"Merged {len(merged)} occupations → {OUT}")

    total = sum(o["employment"] for o in merged)
    print(f"Total workers: {total:,.0f}")


if __name__ == "__main__":
    main()
