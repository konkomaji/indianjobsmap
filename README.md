# Indian Jobs Map

A research tool for visually exploring India's 61.6 crore (616 million) workers by occupation, sector, and AI exposure. Inspired by [karpathy/jobs](https://karpathy.ai/jobs/).

**This is not a report, a paper, or a serious economic publication. It is a development tool for exploring India's labour force data visually.**

Live demo: [konkomaji.github.io/indianjobsmap](https://konkomaji.github.io/indianjobsmap)

Built by [Konko Maji](https://www.linkedin.com/in/konkomaji/), inspired by Andrej Karpathy's US Jobs visualisation.

The interface follows the **Material 3 Expressive** design language with a saffron seed colour: tonal surface containers, pill-shaped filter chips, extra-large rounded corners, and springy motion curves. Fully responsive, with a bottom sheet for occupation details on mobile.

The goal is simple: take Karpathy's idea and build something larger and fully India-specific, so that an ordinary person in India, a student, a job seeker, a teacher, can open it and understand at a glance where the country actually works and how AI might touch each kind of job. It is meant to grow over time as MoSPI releases fresh data.

---

## What it shows

A D3 treemap of **118 occupations** (NCO-2015 3-digit groups) across 9 major groups, covering India's entire **61.6 crore** workforce from the PLFS 2025 unit-level microdata. Each rectangle is one occupation. Size corresponds to the number of workers. Colour can be switched between:

- **AI Exposure** (0 to 10): how much current AI can reshape daily work in this occupation
- **Automation Risk** (0 to 10): physical automation likelihood in India within 10 years
- **Median Wage**: median annual earnings, computed from PLFS 2025 microdata
- **Formalization Potential** (0 to 10): informal to formal employment transition likelihood
- **Gig Platform Potential** (0 to 10): whether this occupation can move to app-based gig work
- **Growth Outlook**: declining, stable, growing, or fast-growing

Click any occupation to see a detailed card with radar chart, India-specific notes, and AI scoring rationale. Every occupation carries a short plain-English note about what the job actually is in India (for example, the kirana shopkeeper facing quick-commerce, the over 1 crore gig delivery riders, the 13 lakh Anganwadi workers).

### Key findings from PLFS 2025

| Fact | Figure |
|---|---|
| Total workers (age 15+, usual status) | 61.6 crore |
| Largest single occupation | Crop farmers (market gardeners), about 13 crore |
| Agriculture sector share of workers | 43.0% (down from 44.8% in 2024) |
| Most AI-exposed large job | Software developers, 9/10 (about 40 lakh workers) |
| Most platformised job | Delivery riders, gig potential 8/10 |
| Lowest median earnings | Subsistence fishers and livestock farmers, under Rs 25,000/year |
| Highest median earnings (in map) | Medical doctors, about Rs 6.1 lakh/year |
| Self-employed share of all workers | 56.2% |
| Informal employment | Over 90% in agriculture and construction labour |

The treemap makes the structure visible instantly: agriculture and elementary work together hold over half of all Indian workers, while the high-paying, high-AI-exposure white-collar jobs (software, finance, engineering) are a small but economically loud sliver.

---

## Important note on data

**The data is hardcoded, not fetched live, but it is built from the real official microdata.**

The occupation-level employment, wages, rural share and informality in this project are computed directly from the **PLFS Calendar Year 2025 first-visit unit-level microdata** (file `CPERV1.txt`, 11,48,634 person records), downloaded from the MoSPI microdata portal. The headline aggregates and earnings benchmarks come from the PLFS Annual Report 2025 press note.

| Source | What it covers | Vintage |
|---|---|---|
| **PLFS 2025 unit-level microdata** (NSO/MoSPI) | Occupation-wise employment, median earnings, rural share, informality, all 118 NCO-2015 groups | Jan-Dec 2025, microdata.gov.in catalog 284 |
| PLFS Annual Report 2025 press note | Headline totals (61.6 Cr workers, LFPR, WPR, UR, sector shares, earnings) | Released 27 March 2026 |
| PLFS Monthly Bulletin April 2026 | Monthly CWS indicators | April 2026 |
| NITI Aayog Gig Economy Report 2022 | Gig and platform worker context | 2022 |
| NASSCOM Annual Report 2024 | IT and ITeS sector context | FY 2023-24 |

**Why not live data?** India does not have a public API for labour-survey microdata. The PLFS unit-level files must be downloaded after a free login and accepting a confidentiality undertaking (the data is anonymised; users agree not to attempt re-identification). The metadata is reachable via the NADA API, but the data files themselves are session-gated. So the pipeline is run locally once, and the compiled `data/occupations.json` and `data/occupations.js` are committed to the repo, so the website works immediately on GitHub Pages without any backend.

---

## How the PLFS 2025 microdata was processed

This is the core of the project. The steps, all reproducible from `pipeline/`:

**1. Obtain the microdata.** From [microdata.gov.in catalog 284](https://microdata.gov.in/NADA/index.php/catalog/284) (Periodic Labour Force Survey, Calendar Year 2025), after login and accepting the confidentiality terms. The person-level file is `CPERV1.txt`, a fixed-width text file of 11,48,634 records, each 371 characters wide.

**2. Read the official byte layout.** The exact column positions come from the official `FV_Data_LayoutPLFS_2025.xlsx` (sheet `CPERV1`), not guesswork. The fields used:

| Field | Bytes | Meaning |
|---|---|---|
| Sector | 15 | 1 = rural, 2 = urban |
| Age | 49-51 | filter to 15+ |
| Principal activity status | 79-80 | UPSS status code |
| Occupation (NCO) principal | 86-88 | NCO-2015 3-digit |
| Subsidiary status / NCO | 99-100 / 106-108 | for subsidiary workers |
| Regular-wage earnings | 322-329 | monthly, Rs |
| Self-employed earnings | 330-337 | monthly, Rs |
| Casual daily earnings | 133-304 | 14 day-activity fields |
| Multiplier (weight) | 341-350 | survey weight x100 |

**3. Apply the survey weights.** Each person record carries a multiplier; the final weight is `MULT / 100` (two implied decimals, per the official README). Workers are persons aged 15+ whose usual activity status (principal, else subsidiary) is a working code (11, 12, 21, 31, 41, 51). Self-employed = 11/12/21, regular wage = 31, casual = 41/51.

**4. Aggregate by occupation.** For each NCO-2015 3-digit code: sum of weights gives employment; rural and informal shares are weight-weighted; median annual earnings is a weighted median (regular and self-employed monthly earnings x12, casual weekly earnings x52).

**5. Calibrate to the official total.** The raw survey weights sum to about **51.9 crore** workers aged 15+ (which matches WPR 57.4% applied to the 90.3 crore surveyed 15+ population). The PLFS Annual Report headline of **61.6 crore** instead applies the WPR to the Ministry of Health projected population. To match the published figure, every occupation count is post-stratified by a single factor of about 1.188. This preserves the occupation shares exactly while making the totals match the press note.

**6. Score and compile.** Each occupation gets AI exposure and India-context scores (see next section), then `5b_compile_2025.py` merges statistics and scores into `data/occupations.json` and `data/occupations.js`.

The result: a treemap of **118 occupations** summing to 61.5 crore workers (within rounding of the official 61.6 crore), broken down by major group as follows: Agriculture 21.6 Cr, Elementary 13.5 Cr, Service and Sales 7.9 Cr, Craft and Trades 7.0 Cr, Machine Operators 3.6 Cr, Professionals 3.4 Cr, Managers 1.6 Cr, Technicians 1.5 Cr, Clerical 1.4 Cr.

**Caveat on comparability:** PLFS was revamped from January 2025 (calendar-year cycle, monthly bulletins, rotational panel, about 2.72 lakh households, roughly 2.65 times the earlier sample). NSO advises caution when comparing 2025 estimates with the July-June rounds up to 2023-24.

---

## AI Exposure scoring

All 118 occupations are scored on a **Karpathy-style 0 to 10 anchored scale adapted for India**. Two scoring paths produce the same schema:

- **Offline labour-economist scores** in `pipeline/scores_2025.py`. Every NCO-2015 group is scored by reasoning over the anchored scale in the Indian context, with a one-line rationale and a plain-English India note. This is the default, so the visualisation is always complete even without an API key.
- **LLM scores** via `pipeline/4_score.py`, which calls **Claude Haiku** (`claude-haiku-4-5-20251001`) with the prompt below when an `ANTHROPIC_API_KEY` is set. These can replace the offline scores.

The anchored scale (also used verbatim in the Haiku prompt):

### The scoring prompt

```
Rate the AI Exposure of this Indian occupation on a scale from 0 to 10.

Consider how much current AI (large language models, vision systems, code generation, voice AI)
can already reshape the daily work of someone in this occupation in India today.

Anchor points:
- 0: No exposure. Work is entirely physical, outdoors, or involves direct human service with no
     digital component. Examples: agricultural labourer harvesting crops, mason laying bricks,
     sanitation worker.
- 1: Very low. Mostly physical work with minor administrative tasks. AI has no meaningful path
     to reshape daily work. Examples: small-scale crop farmer, construction helper, dairy farmer.
- 2: Low. Primary work is manual with occasional basic digital use such as a phone for UPI
     payments or navigation. Examples: electrician doing home wiring, auto-rickshaw driver,
     domestic cook.
- 3: Moderate-low. Some digital tools used but core work remains physical. Gig platforms
     have digitised dispatch but not execution. Examples: Swiggy or Zomato delivery rider,
     plumber on Urban Company, security guard.
- 4: Moderate. Mix of physical and digital tasks. AI can assist with paperwork, scheduling,
     or research but cannot replace fieldwork. Examples: primary school teacher, staff nurse,
     field sales representative.
- 5: Moderate. Roughly equal physical and digital work. AI tools beginning to augment a
     significant portion of daily output. Examples: accountant in a small firm, insurance agent,
     medical imaging technician.
- 6: Moderate-high. Majority of work is digital or knowledge-based. AI tools actively being
     adopted. Core tasks are in domains AI is improving. Examples: journalist, marketing executive,
     HR manager, social media manager.
- 7: High. Primarily digital or knowledge work. AI can handle significant portions of daily output.
     Worker productivity is being reshaped by AI tools. Examples: civil engineer (design and
     analysis), financial analyst, paralegal, translator.
- 8: Very high. Almost entirely digital. AI tools already replacing meaningful portions of the
     workload. Workers who do not adapt will face displacement. Examples: content writer, graphic
     designer, software tester, BPO data analyst.
- 9: Near-maximum. The job is almost entirely done on a computer. All core tasks, including
     writing, coding, analysing, designing, and communicating, are in domains where AI is rapidly
     improving. The occupation faces major restructuring. Examples: software developer, data analyst,
     copywriter, graphic designer.
- 10: Maximum. Routine information processing, fully digital, no physical component. AI can already
      do most of it today. Examples: data entry clerk, BPO voice agent, telemarketer,
      form processing operator.

Important India context for AI Exposure:
- Score based on actual AI adoption likelihood in India, not theoretical global maximum
- Account for lower digital infrastructure in rural and informal workforces
- A rural primary teacher scores lower than a Bengaluru IT trainer due to infrastructure gaps
- Factor in whether workers in this occupation typically have devices, connectivity, and literacy
  to use AI tools in India today

Respond with ONLY a JSON object in this exact format, no other text:
{"ai_exposure": <0-10>, "ai_rationale": "<2-3 sentences explaining the key factors in Indian context>",
 "automation_risk": <0-10>, "formalization_potential": <0-10>, "gig_potential": <0-10>,
 "growth_outlook": "<declining|stable|growing|fast-growing>"}
```

### Caveat on AI Exposure scores

These are rough estimates from an LLM, not rigorous predictions. A high score does not mean the job will disappear. Software developers score 9/10 because AI is already reshaping their work, but demand for software keeps growing as each developer becomes more productive. The score does not account for demand elasticity, latent demand, regulatory barriers, or the specific realities of India's largely informal economy. Many high-exposure occupations will be reshaped rather than replaced.

---

## Pipeline

```
pipeline/
  6_parse_plfs2025.py   Parse PLFS 2025 CPERV1.txt microdata into per-NCO stats (CURRENT)
  scores_2025.py        AI exposure + India scores for all NCO-2015 groups
  5b_compile_2025.py    Merge 2025 stats + scores into occupations.json/.js (CURRENT)

  # earlier / alternative scripts
  1_fetch_ncs.py        Scrape NCS portal for occupation descriptions (optional)
  2_parse_plfs.py       Parse older PLFS fixed-width microdata (2023-24 layout)
  3_extract.py          Merge PLFS stats with NCS descriptions
  4_score.py            Score via Claude Haiku when ANTHROPIC_API_KEY is set
  5_compile.py          Older compile step
```

### Current workflow (PLFS 2025)

**Step 1: Get the microdata.** Log in at microdata.gov.in, open [catalog 284](https://microdata.gov.in/NADA/index.php/catalog/284), accept the confidentiality undertaking, download the unit-level archive, and place `CPERV1.txt` in `data/raw/plfs/`. The official documentation (byte layout, README, schedules) is already in `data/raw/plfs2025_docs/`.

**Step 2: Parse and update.**

```bash
python pipeline/6_parse_plfs2025.py            # dry run, prints calibration report
python pipeline/6_parse_plfs2025.py --apply    # writes per-NCO stats
```

This reads the official byte layout, applies survey weights, aggregates by NCO-2015 code, calibrates to the 61.6 crore official total, and writes `data/processed/plfs2025_by_nco.json`.

**Step 3: Compile the final dataset.**

```bash
python pipeline/5b_compile_2025.py
```

Merges the parsed statistics with the scores in `scores_2025.py` and writes `data/occupations.json` and `data/occupations.js`. The `.js` file wraps the JSON as `window.JOBS_DATA = {...}` so the frontend works on `file://` and on GitHub Pages without a server.

**Optional: re-score with Claude Haiku.** Set `ANTHROPIC_API_KEY` in `.env` and run `python pipeline/4_score.py` to replace the offline scores with LLM scores.

---

## Running locally

No build step needed. The frontend is plain HTML, CSS, and JavaScript.

```bash
# Option 1: open index.html directly in browser (uses occupations.js)
# Just double-click index.html

# Option 2: serve with Python for proper fetch() support
python -m http.server 8000
# then open http://localhost:8000
```

---

## Tech stack

| Layer | What |
|---|---|
| Frontend | Vanilla JS, D3 v7, Poppins (Google Fonts) |
| Design | Material 3 Expressive (saffron seed, tonal surfaces, spring motion) |
| Treemap | D3 treemap (squarify, power-scaled employment) |
| Info card | D3 SVG radar chart, M3 elevated card, mobile bottom sheet |
| Data | PLFS 2025 microdata, compiled to JSON, loaded as JS global for file:// compat |
| Scoring | Python 3.10+; offline anchored scoring, optional Claude Haiku |
| Hosting | GitHub Pages (static, no build step) |

---

## Data limitations

- **PLFS sample size**: some NCO 3-digit codes have small sample sizes. National estimates are reliable; the smallest occupations (under about 1 lakh workers) are dropped from the map.
- **Informal sector wages**: PLFS captures regular wage and salaried earnings reliably. Self-employed and casual incomes are harder to measure and may be underestimated; subsistence farmers often report near-zero earnings.
- **Post-stratification**: occupation counts are scaled by a single factor (about 1.188) so the total matches the official 61.6 crore. This preserves shares exactly but assumes uniform scaling across occupations.
- **Gig workers**: platform workers are classified under delivery and transport NCOs in PLFS. Dedicated gig counts (over 1 crore, NITI Aayog) are projections, not survey enumeration.
- **Comparability**: PLFS 2025 used a revamped survey design and is not strictly comparable with rounds up to 2023-24.

---

## Roadmap

Indian Jobs Map is meant to grow into the most complete, India-specific picture of who works at what, refreshed as MoSPI releases new data. Planned directions:

- **Auto-refresh on new PLFS data**: re-run the pipeline whenever a new annual or quarterly PLFS round lands, so the map stays current within weeks of release.
- **State-level view**: drill into any state, using the PLFS state tables (Jan-Mar 2026 already collected) and state-wise microdata.
- **Gender and rural/urban toggles**: split every occupation by male/female and rural/urban, the data is already in the microdata.
- **Time slider**: show how each occupation's size, wage and informality has moved across PLFS rounds.
- **Alternative colourings**: robotics exposure, offshoring risk, climate-transition impact, and skill-shortage severity, each a re-run of the scoring prompt.
- **Wage and education layers**: add education-level and earnings-distribution views per occupation.
- **Vernacular labels**: Hindi and other Indian-language occupation names so the tool is readable for everyone, not only English speakers.

---

## Acknowledgements

- [Andrej Karpathy](https://karpathy.ai/jobs/) for the original US jobs visualisation concept and scoring prompt structure
- NSO / MoSPI (Ministry of Statistics and Programme Implementation) for PLFS unit-level microdata, via [microdata.gov.in](https://microdata.gov.in)
- NITI Aayog for gig-economy estimates
- NASSCOM for IT sector context
- [Material 3 Expressive](https://m3.material.io/) design guidelines by Google

---

## License

MIT for the code. The compiled data files in `data/` are derived from PLFS unit-level microdata published by NSO/MoSPI; the underlying data is subject to MoSPI's terms of use. Only anonymised, aggregated occupation-level figures are published here; no microdata is redistributed.
