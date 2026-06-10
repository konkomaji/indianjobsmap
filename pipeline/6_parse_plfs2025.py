#!/usr/bin/env python3
"""
Parse PLFS Calendar Year 2025 first-visit person-level microdata (CPERV1.txt)
and update the treemap occupation data in data/occupations.json + .js.

DATA DOWNLOAD (login required, free account):
  1. Register/login at https://microdata.gov.in/NADA/index.php/auth/login
  2. Open catalog entry 284: Periodic Labour Force Survey (PLFS),
     Calendar Year 2025 (Jan-Dec25)
     https://microdata.gov.in/NADA/index.php/catalog/284/get-microdata
  3. Download the unit-level data archive, extract CPERV1.txt
  4. Place it at: data/raw/plfs/CPERV1.txt

Byte layout from "2. FV_Data_LayoutPLFS_2025.xlsx" (CPERV1 sheet), already
downloaded to data/raw/plfs2025_docs/. Record length 371+1. 1,148,634 records.

Weight handling (verified against the data):
  Final Weight = MULT / 100   (MULT at bytes 341-350, two implied decimals)
  The pooled weights sum to ONE annual-average national cross-section
  (15+ population about 90.3 crore), no division by 12 needed.
  Survey-weighted workers 15+ come to about 51.6 crore, which matches
  WPR 57.4% x 90.3 crore. The press-note figure of 61.6 crore workers
  instead applies WPR to the MoHFW projected population, so employment
  counts are post-stratified: scaled by 616,000,000 / survey worker total.

Usage:
  python pipeline/6_parse_plfs2025.py            # parse + report only
  python pipeline/6_parse_plfs2025.py --apply    # also update data/occupations.json/.js
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
RAW = ROOT / "data" / "raw" / "plfs"
OUT_STATS = ROOT / "data" / "processed" / "plfs2025_by_nco.json"
OCC_JSON = ROOT / "data" / "occupations.json"
OCC_JS = ROOT / "data" / "occupations.js"

# ── CPERV1.txt byte positions (1-based start, inclusive end) ──
# from FV_Data_LayoutPLFS_2025.xlsx sheet CPERV1
F = {
    "sector":   (15, 15),    # 1=rural 2=urban
    "sex":      (48, 48),
    "age":      (49, 51),
    "pas":      (79, 80),    # principal usual activity status
    "ocu_pas":  (86, 88),    # NCO-2015 3-digit, principal
    "sas":      (99, 100),   # subsidiary activity status
    "ocu_sas":  (106, 108),  # NCO-2015 3-digit, subsidiary
    "ern_reg":  (322, 329),  # monthly earnings, regular wage (Rs, whole)
    "ern_self": (330, 337),  # monthly earnings, self-employed (Rs, whole)
    "mult":     (341, 350),  # weight x100
}
# 14 daily-earning fields for casual workers (CWS week, Rs per day)
CASUAL_ERN = [(133,137),(144,148),(159,163),(170,174),(185,189),(196,200),
              (211,215),(222,226),(237,241),(248,252),(263,267),(274,278),
              (289,293),(300,304)]

WORKING = {"11","12","21","31","41","51"}   # UPSS working status codes
SELF_EMP = {"11","12","21"}
REGULAR  = {"31"}
CASUAL   = {"41","51"}
OFFICIAL_WORKERS = 616_000_000   # PLFS AR 2025 press note, 15+, MoHFW population

# NCO-2015 3-digit names (subset; unknown codes fall back to NCO-XXX)
NCO_NAMES = {
    "111": "Legislators & Senior Officials", "112": "Managing Directors & CEOs",
    "121": "Business & Admin Managers", "122": "Sales & PR Managers",
    "131": "Production Managers (Agri & Industry)", "132": "Manufacturing & Construction Managers",
    "134": "Professional Services Managers", "141": "Hotel & Restaurant Managers",
    "142": "Retail & Wholesale Trade Managers", "143": "Other Services Managers",
    "211": "Physical & Earth Scientists", "212": "Mathematicians & Statisticians",
    "213": "Life Scientists", "214": "Engineering Professionals",
    "215": "Electrotechnology Engineers", "216": "Architects & Designers",
    "221": "Medical Doctors", "222": "Nursing & Midwifery Professionals",
    "223": "Traditional Medicine Professionals", "225": "Veterinarians",
    "226": "Other Health Professionals", "231": "University & Higher Ed Teachers",
    "232": "Vocational Education Teachers", "233": "Secondary Teachers",
    "234": "Primary & Pre-Primary Teachers", "235": "Other Teaching Professionals",
    "241": "Finance Professionals", "242": "Administration Professionals",
    "243": "Sales & Marketing Professionals", "251": "Software & Applications Developers",
    "252": "Database & Network Professionals", "261": "Legal Professionals",
    "262": "Librarians & Archivists", "263": "Social & Religious Professionals",
    "264": "Authors, Journalists & Linguists", "265": "Creative & Performing Artists",
    "311": "Science & Engineering Technicians", "313": "Process Control Technicians",
    "315": "Ship & Aircraft Controllers", "321": "Medical & Pharma Technicians",
    "322": "Nursing & Midwifery Associates", "325": "Other Health Associates",
    "331": "Finance & Maths Associates", "332": "Sales & Purchasing Agents",
    "333": "Business Services Agents", "334": "Admin & Specialised Secretaries",
    "335": "Govt Regulatory Associates", "341": "Legal & Social Associates",
    "342": "Sports & Fitness Workers", "343": "Artistic & Culinary Associates",
    "351": "ICT Operations Technicians", "352": "Telecom & Broadcasting Technicians",
    "411": "General Office Clerks", "412": "Secretaries", "413": "Keyboard Operators",
    "421": "Cashiers, Tellers & Collectors", "422": "Client Information Clerks",
    "431": "Accounting & Numerical Clerks", "432": "Stores & Transport Clerks",
    "441": "Other Clerical Workers",
    "511": "Travel Attendants & Guides", "512": "Cooks",
    "513": "Waiters & Bartenders", "514": "Hairdressers & Beauticians",
    "515": "Building Caretakers & Housekeepers", "516": "Other Personal Services",
    "521": "Street & Market Salespersons", "522": "Shopkeepers & Shop Sales",
    "523": "Cashiers & Ticket Clerks", "524": "Other Sales Workers",
    "531": "Childcare Workers & Teacher Aides", "532": "Personal Care (Health) Workers",
    "541": "Protective Services Workers",
    "611": "Market Gardeners & Crop Growers", "612": "Animal Producers",
    "613": "Mixed Crop & Animal Producers", "621": "Forestry Workers",
    "622": "Fishery Workers & Hunters",
    "631": "Subsistence Crop Farmers", "632": "Subsistence Livestock Farmers",
    "633": "Subsistence Mixed Farmers", "634": "Subsistence Fishers",
    "711": "Building Frame Workers (Masons)", "712": "Building Finishers",
    "713": "Painters & Building Cleaners", "721": "Sheet & Structural Metal Workers",
    "722": "Blacksmiths & Toolmakers", "723": "Machinery Mechanics & Repairers",
    "731": "Handicraft & Precision Workers", "732": "Printing Trades Workers",
    "741": "Electrical Equipment Workers", "742": "Electronics & Telecom Installers",
    "751": "Food Processing Workers", "752": "Wood Treaters & Cabinet Makers",
    "753": "Garment & Related Trades", "754": "Other Craft Workers",
    "811": "Mining & Mineral Plant Operators", "812": "Metal Processing Operators",
    "813": "Chemical & Photo Plant Operators", "814": "Rubber, Plastic & Paper Operators",
    "815": "Textile & Fur Machine Operators", "816": "Food Machine Operators",
    "817": "Wood & Paper Plant Operators", "818": "Other Plant Operators",
    "821": "Assemblers", "831": "Locomotive Drivers", "832": "Car & Van Drivers",
    "833": "Truck & Bus Drivers", "834": "Mobile Plant Operators", "835": "Ship Deck Crews",
    "911": "Domestic & Hotel Cleaners", "912": "Vehicle & Window Cleaners",
    "921": "Agricultural & Fishery Labourers", "931": "Mining & Construction Labourers",
    "932": "Manufacturing Labourers", "933": "Transport & Storage Labourers",
    "941": "Food Preparation Assistants", "951": "Street Service Workers",
    "952": "Street Vendors (non-food)", "961": "Refuse Workers",
    "962": "Other Elementary Workers (incl. delivery)",
}
MAJOR_NAMES = {
    "1": "Managers", "2": "Professionals", "3": "Technicians",
    "4": "Clerical Support", "5": "Service & Sales", "6": "Agriculture",
    "7": "Craft & Trades", "8": "Machine Operators", "9": "Elementary",
}


def cut(line, pos):
    a, b = pos
    return line[a-1:b]


def parse_file(path):
    """Stream-parse CPERV1.txt, return per-NCO accumulators."""
    from collections import defaultdict
    acc = defaultdict(lambda: {
        "w": 0.0, "w_rural": 0.0, "w_casual": 0.0, "w_self": 0.0, "w_reg": 0.0,
        "wages": [],   # (annual_wage, weight) samples
        "n": 0,
    })
    total_w15 = 0.0
    n_lines = 0

    with open(path, "r", encoding="latin-1", errors="replace") as f:
        for line in f:
            n_lines += 1
            if len(line) < 350:
                continue
            mult = cut(line, F["mult"]).strip()
            if not mult.isdigit():
                continue
            w = int(mult) / 100.0

            age_s = cut(line, F["age"]).strip()
            age = int(age_s) if age_s.isdigit() else 0
            if age < 15:
                continue   # headline workforce is 15+

            pas = cut(line, F["pas"]).strip()
            sas = cut(line, F["sas"]).strip()

            # UPSS worker: principal working, else subsidiary working
            if pas in WORKING:
                status, nco = pas, cut(line, F["ocu_pas"]).strip()
            elif sas in WORKING:
                status, nco = sas, cut(line, F["ocu_sas"]).strip()
            else:
                continue

            total_w15 += w

            if len(nco) != 3 or not nco.isdigit() or nco[0] == "0":
                continue

            a = acc[nco]
            a["w"] += w
            a["n"] += 1
            if cut(line, F["sector"]) == "1":
                a["w_rural"] += w
            if status in CASUAL:
                a["w_casual"] += w
            elif status in SELF_EMP:
                a["w_self"] += w
            elif status in REGULAR:
                a["w_reg"] += w

            # annualised earnings sample
            annual = 0
            if status in REGULAR:
                e = cut(line, F["ern_reg"]).strip().lstrip("-")
                if e.isdigit() and int(e) > 0:
                    annual = int(e) * 12
            elif status in SELF_EMP:
                e = cut(line, F["ern_self"]).strip().lstrip("-")
                if e.isdigit() and int(e) > 0:
                    annual = int(e) * 12
            else:  # casual: sum of daily earnings over CWS week -> annualise
                wk = 0
                for pos in CASUAL_ERN:
                    e = cut(line, pos).strip()
                    if e.isdigit():
                        wk += int(e)
                if wk > 0:
                    annual = wk * 52
            if annual > 0:
                a["wages"].append((annual, w))

    return acc, total_w15, n_lines


def weighted_median(pairs):
    if not pairs:
        return 0
    pairs.sort(key=lambda x: x[0])
    half = sum(p[1] for p in pairs) / 2
    run = 0.0
    for v, w in pairs:
        run += w
        if run >= half:
            return int(v)
    return int(pairs[-1][0])


def main():
    apply_update = "--apply" in sys.argv

    path = RAW / "CPERV1.txt"
    if not path.exists():
        alt = list(RAW.glob("*PERV1*.txt")) + list(RAW.glob("*PERV1*.TXT"))
        if alt:
            path = alt[0]
        else:
            print(f"CPERV1.txt not found in {RAW}")
            print(__doc__.split("Byte layout")[0])
            return

    print(f"Parsing {path.name} ...")
    acc, total_w15, n_lines = parse_file(path)
    print(f"  {n_lines:,} lines read")
    print(f"  Survey-weighted workers 15+: {total_w15/1e7:.1f} crore "
          f"(expected about 51.6 crore = WPR 57.4% x 90.3 crore)")
    if not (45e7 < total_w15 < 60e7):
        print("  WARNING: total far from benchmark, check layout/weights")

    # Post-stratify to the official press-note total (MoHFW population base)
    scale = OFFICIAL_WORKERS / total_w15
    print(f"  Post-stratification scale: x{scale:.3f} "
          f"-> {OFFICIAL_WORKERS/1e7:.1f} crore official total")

    results = []
    for nco, a in acc.items():
        if a["w"] * scale < 100000:   # skip occupations under 1 lakh workers
            continue
        results.append({
            "code": nco,
            "name": NCO_NAMES.get(nco, f"NCO-{nco}"),
            "major_group": nco[0],
            "major_group_name": MAJOR_NAMES.get(nco[0], "Other"),
            "employment": int(a["w"] * scale),
            "median_wage": weighted_median(a["wages"]),
            "rural_pct": round(100 * a["w_rural"] / a["w"]),
            "informal_pct": round(100 * (a["w_casual"] + a["w_self"]) / a["w"]),
            "sample_n": a["n"],
            "data_vintage": "PLFS 2025 (Jan-Dec)",
        })
    results.sort(key=lambda x: -x["employment"])

    OUT_STATS.parent.mkdir(parents=True, exist_ok=True)
    OUT_STATS.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"  {len(results)} NCO groups -> {OUT_STATS}")
    print(f"  Top 5: " + ", ".join(f"{r['name']} ({r['employment']/1e7:.1f}Cr)"
                                   for r in results[:5]))

    if not apply_update:
        print("\nDry run done. Re-run with --apply to update the treemap data.")
        return

    # ── Update occupations.json: refresh stats on matching NCO codes ──
    occ = json.loads(OCC_JSON.read_text(encoding="utf-8"))
    by_code = {r["code"]: r for r in results}
    updated = 0
    for o in occ["occupations"]:
        r = by_code.get(o["code"])
        if not r:
            continue
        o["employment"] = r["employment"]
        if r["median_wage"] > 0:
            o["median_wage"] = r["median_wage"]
        o["rural_pct"] = r["rural_pct"]
        o["informal_pct"] = r["informal_pct"]
        o["data_vintage"] = "PLFS 2025 (Jan-Dec)"
        updated += 1

    occ["meta"]["data_vintage"] = "PLFS Calendar Year 2025 unit-level microdata (first visit)"
    occ["meta"]["total_workers"] = 616000000
    occ["meta"]["note"] = ("Occupation-level employment, wages, rural share and "
                           "informality re-estimated from PLFS CY2025 first-visit "
                           "unit-level microdata (CPERV1.txt, weights MULT/100, "
                           "12 pooled monthly cross-sections).")

    js = json.dumps(occ, indent=2, ensure_ascii=False)
    OCC_JSON.write_text(js, encoding="utf-8")
    OCC_JS.write_text("/* Auto-generated — do not edit manually */\n"
                      "window.JOBS_DATA = " + js + ";\n", encoding="utf-8")
    print(f"\nApplied: {updated}/{len(occ['occupations'])} occupations updated "
          f"-> {OCC_JSON.name}, {OCC_JS.name}")


if __name__ == "__main__":
    main()
