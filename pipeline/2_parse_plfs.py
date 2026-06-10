#!/usr/bin/env python3
"""
Parse PLFS (Periodic Labour Force Survey) unit-level microdata.
Produces employment counts, median wages, rural %, informal % by NCO-2015 3-digit code.

DATA DOWNLOAD:
  1. Visit: https://mospi.gov.in/web/plfs (Annual Reports section)
  2. Download unit-level data for latest year (e.g. 2022-23)
  3. Place files in: data/raw/plfs/
  Files: person_visit1.txt, person_visit2.txt (or .dta Stata format)

PLFS key variables (NCO-2015, person records):
  Sector (rural=1/urban=2), Sex, Age, Education, UPSS activity status,
  NIC-2008 industry code, NCO-2015 occupation code, Employment type,
  Weekly wages, Survey multiplier (MULT_CWS)

Reference: PLFS Annual Report Appendix (data layout/variable list)
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "plfs"
OUT = Path(__file__).parent.parent / "data" / "processed" / "plfs_by_nco.json"

# NCO 3-digit code to name mapping (NCO-2015)
# Full list: https://mospi.gov.in/sites/default/files/nco_2015.pdf
NCO_NAMES = {
    "111": "Senior Officials & Legislators",
    "121": "Corporate Managers",
    "131": "Production & Operations Managers",
    "141": "Hotel & Restaurant Managers",
    "211": "Physical & Earth Scientists",
    "212": "Mathematicians & Statisticians",
    "213": "Life Scientists",
    "214": "Engineers",
    "215": "Ship & Aircraft Officers",
    "221": "Medical Doctors",
    "222": "Nursing & Midwifery",
    "223": "Traditional & Allied Health",
    "231": "University Teachers",
    "232": "Vocational Teachers",
    "233": "Secondary Teachers",
    "234": "Primary Teachers",
    "235": "Other Teaching Professionals",
    "241": "Finance Professionals",
    "242": "Administration Professionals",
    "243": "Sales & Marketing Professionals",
    "251": "Software & IT Professionals",
    "261": "Legal Professionals",
    "262": "Archivists & Librarians",
    "311": "Science & Engineering Technicians",
    "321": "Medical Technicians",
    "331": "Finance & Admin Technicians",
    "341": "Business Agents",
    "351": "ICT Technicians",
    "411": "General Office Clerks",
    "412": "Secretaries",
    "421": "Cashiers & Tellers",
    "422": "Information Clerks",
    "431": "Numerical Clerks",
    "432": "Data Entry Clerks",
    "511": "Flight Attendants & Guides",
    "512": "Cooks",
    "513": "Waiters & Servers",
    "514": "Bartenders",
    "516": "Security Guards",
    "521": "Market Stall Sellers",
    "522": "Shop Keepers",
    "524": "Retail Salespersons",
    "531": "Childcare Workers",
    "532": "Healthcare Assistants",
    "541": "Armed Forces",
    "611": "Crop Farmers",
    "612": "Animal Farmers",
    "613": "Mixed Farmers",
    "621": "Forestry Workers",
    "622": "Charcoal Burners",
    "631": "Fishers",
    "632": "Hunters & Trappers",
    "711": "Miners & Quarry Workers",
    "712": "Building Constructors",
    "713": "Building Finishers",
    "721": "Sheet Metal Workers",
    "722": "Blacksmiths & Toolmakers",
    "731": "Precision Instrument Makers",
    "732": "Potters & Glass Workers",
    "741": "Electricians",
    "742": "Electronics Technicians",
    "751": "Food Processing Workers",
    "752": "Wood & Paper Workers",
    "753": "Garment Workers",
    "771": "Craft Workers",
    "811": "Mining Equipment Operators",
    "821": "Industrial Plant Operators",
    "831": "Locomotive Operators",
    "832": "Car & Motorcycle Drivers",
    "833": "Truck & Bus Drivers",
    "834": "Mobile Plant Operators",
    "911": "Domestic Cleaners",
    "912": "Vehicle Cleaners",
    "921": "Agricultural Laborers",
    "931": "Construction Laborers",
    "941": "Food Laborers",
    "951": "Street Vendors (support)",
    "961": "Refuse Workers",
    "962": "Delivery Workers",
    "991": "Other Elementary Workers",
}

NCO_MAJOR = {str(i): str(i)[0] for i in range(100, 1000)}
MAJOR_NAMES = {
    "1": "Managers", "2": "Professionals", "3": "Technicians",
    "4": "Clerical Support", "5": "Service & Sales", "6": "Agriculture",
    "7": "Craft & Trades", "8": "Machine Operators", "9": "Elementary",
}

# Employment type: 1=self-employed, 2=regular wage, 3=casual labor
INFORMAL_TYPES = {3}  # casual labor = informal; self-employed = debatable


def load_plfs_fixed_width(filepath):
    """
    Load PLFS person-level fixed-width text file.
    Column positions from PLFS data dictionary (Annual Report Appendix).
    ADJUST positions based on actual year's data dictionary.
    """
    # These positions are approximate — verify against your year's data dictionary
    colspecs = [
        (0,  2,  "state"),
        (3,  5,  "district"),
        (5,  6,  "sector"),      # 1=rural, 2=urban
        (20, 22, "sex"),          # 1=male, 2=female
        (22, 24, "age"),
        (26, 28, "education"),    # 01=not literate, ..., 13=post-grad
        (35, 37, "upss_status"),  # usual principal activity
        (38, 42, "nic_code"),     # NIC-2008 4-digit industry
        (42, 46, "nco_code"),     # NCO-2015 4-digit occupation
        (46, 47, "emp_type"),     # 1=self-emp, 2=regular, 3=casual
        (85, 91, "wages"),        # weekly wages in Rs (0 if non-wage)
        (95, 105, "multiplier"),  # survey weight
    ]

    names = [c[2] for c in colspecs]
    specs = [(c[0], c[1]) for c in colspecs]

    df = pd.read_fwf(
        filepath,
        colspecs=specs,
        names=names,
        dtype=str,
        encoding="latin-1"
    )

    # Convert numeric columns
    for col in ["age", "wages", "multiplier"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["sector"] = pd.to_numeric(df["sector"], errors="coerce")
    df["emp_type"] = pd.to_numeric(df["emp_type"], errors="coerce")
    df["nco_3digit"] = df["nco_code"].str[:3].str.strip()

    # Workers only: filter by usual activity (11-72 are working categories in UPSS)
    df["upss_num"] = pd.to_numeric(df["upss_status"], errors="coerce")
    df = df[df["upss_num"].between(11, 72)]

    return df


def aggregate_by_nco(df):
    """Aggregate employment stats by NCO 3-digit code."""
    results = []
    grouped = df.groupby("nco_3digit")

    for nco, grp in grouped:
        if len(nco) != 3 or not nco.isdigit():
            continue

        total_employment = int(grp["multiplier"].sum())
        if total_employment < 10000:  # skip tiny groups
            continue

        # Median wage (annualized from weekly, exclude zeros)
        wage_workers = grp[grp["wages"] > 0]
        if len(wage_workers) > 0:
            # Weighted median
            wages_sorted = wage_workers.sort_values("wages")
            cumsum = wages_sorted["multiplier"].cumsum()
            median_idx = cumsum.searchsorted(cumsum.iloc[-1] / 2)
            weekly_median = float(wages_sorted["wages"].iloc[min(median_idx, len(wages_sorted)-1)])
            annual_median = int(weekly_median * 52)
        else:
            annual_median = 0

        rural_workers = grp[grp["sector"] == 1]["multiplier"].sum()
        rural_pct = int(100 * rural_workers / grp["multiplier"].sum()) if total_employment > 0 else 50

        informal_workers = grp[grp["emp_type"].isin(INFORMAL_TYPES)]["multiplier"].sum()
        informal_pct = int(100 * informal_workers / grp["multiplier"].sum()) if total_employment > 0 else 50

        results.append({
            "code": nco,
            "name": NCO_NAMES.get(nco, f"NCO-{nco}"),
            "major_group": nco[0],
            "major_group_name": MAJOR_NAMES.get(nco[0], "Other"),
            "employment": total_employment,
            "median_wage": annual_median,
            "rural_pct": rural_pct,
            "informal_pct": informal_pct,
        })

    return sorted(results, key=lambda x: -x["employment"])


def main():
    plfs_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.TXT"))

    if not plfs_files:
        print(f"No PLFS data files found in {RAW_DIR}")
        print("Download PLFS unit-level data from https://mospi.gov.in/web/plfs")
        print("Place .txt person record files in data/raw/plfs/")
        return

    print(f"Found {len(plfs_files)} PLFS files")
    all_dfs = []
    for f in plfs_files:
        print(f"  Loading {f.name}...")
        try:
            df = load_plfs_fixed_width(f)
            all_dfs.append(df)
            print(f"    {len(df):,} person records")
        except Exception as e:
            print(f"    ERROR: {e}")

    if not all_dfs:
        print("No data loaded. Check file format and column positions.")
        return

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal records: {len(combined):,}")

    results = aggregate_by_nco(combined)
    print(f"NCO groups: {len(results)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Saved → {OUT}")

    total = sum(r["employment"] for r in results)
    print(f"Total workers tracked: {total:,}")


if __name__ == "__main__":
    main()
