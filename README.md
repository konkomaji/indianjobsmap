# Indian Jobs Map

A research tool for visually exploring India's 563 million workers by occupation, sector, and AI exposure. Inspired by [karpathy/jobs](https://karpathy.ai/jobs/).

**This is not a report, a paper, or a serious economic publication. It is a development tool for exploring India's labour force data visually.**

Live demo: [konkomaji.github.io/indianjobsmap](https://konkomaji.github.io/indianjobsmap)

Built by **Konko Maji**, inspired by Andrej Karpathy's US Jobs visualisation.

---

## What it shows

A D3 treemap of 40 occupations across 9 major groups (NCO-2015 classification). Each rectangle is one occupation. Size corresponds to number of workers. Colour can be switched between:

- **AI Exposure** (0 to 10): how much current AI can reshape daily work in this occupation
- **Automation Risk** (0 to 10): physical automation likelihood in India within 10 years
- **Median Wage**: annualised from PLFS weekly earnings
- **Formalization Potential** (0 to 10): informal to formal employment transition likelihood
- **Gig Platform Potential** (0 to 10): whether this occupation can move to app-based gig work
- **Growth Outlook**: declining, stable, growing, or fast-growing

Click any occupation to see a detailed card with radar chart, India-specific notes, and AI scoring rationale.

---

## Important note on data

**The data is hardcoded, not fetched live.**

India's official labour statistics are released with significant delays. The PLFS (Periodic Labour Force Survey) is published annually by MoSPI, but the unit-level microdata typically arrives 12 to 18 months after the survey period ends. The raw microdata requires registration on the MoSPI portal and is distributed as fixed-width text files with a data dictionary appendix.

The figures in this project are sourced from:

| Source | What it covers | Vintage |
|---|---|---|
| PLFS 2023-24 (MoSPI) | Employment counts, wages, rural share, employment type | Released 2025 |
| QES Q3 2024 (Labour Bureau) | Organised sector employment by industry | Q3 2024 |
| NASSCOM Annual Report 2024 | IT and ITeS sector headcount | FY 2023-24 |
| NITI Aayog Gig Economy Report 2022 | Gig and platform worker estimates | 2022 |
| Labour Bureau Construction Survey | Construction sector wage data | 2023 |

**Why not live data?** India does not have a public API for labour statistics. PLFS microdata must be manually downloaded after registration. Employment figures for informal sectors like agriculture and construction are survey-estimated, not enumerated. Many occupation categories used here combine multiple NCO-2015 sub-codes to produce usable sample sizes. The pipeline to reproduce the data from scratch is included (see below), but the compiled `data/occupations.json` and `data/occupations.js` are committed to the repo so the frontend works immediately without running anything.

---

## AI Exposure scoring

Occupations were scored using **Claude Haiku** (`claude-haiku-4-5-20251001`) via the Anthropic API. The scoring prompt uses a Karpathy-style 0 to 10 anchored scale adapted for India:

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

The `pipeline/` folder contains scripts to regenerate the data from scratch if you have access to the raw PLFS microdata.

```
pipeline/
  1_fetch_ncs.py      Scrapes NCS portal for occupation descriptions (optional)
  2_parse_plfs.py     Parses PLFS fixed-width unit-level microdata into per-NCO stats
  3_extract.py        Merges PLFS stats with NCS descriptions
  4_score.py          Scores each occupation via Claude Haiku (Karpathy-style prompt)
  5_compile.py        Compiles final occupations.json for the frontend
```

### Step 1 (optional): Fetch NCS descriptions

```bash
python pipeline/1_fetch_ncs.py
```

Scrapes [ncs.gov.in](https://ncs.gov.in) for occupation descriptions by sector. This is optional. If you skip it, occupations will have no long description.

### Step 2: Parse PLFS microdata

```bash
python pipeline/2_parse_plfs.py
```

**Requires raw PLFS data.** Download unit-level person records from [mospi.gov.in/web/plfs](https://mospi.gov.in/web/plfs) (Annual Reports section, unit-level data tab). After registration and approval, place the `.txt` files in `data/raw/plfs/`. The script produces per-NCO employment counts, median wages, rural share, and informality rate.

Note: PLFS fixed-width column positions vary by year. Always check the data dictionary appendix in the Annual Report PDF and update `colspecs` in `2_parse_plfs.py` accordingly.

### Step 3: Merge

```bash
python pipeline/3_extract.py
```

Merges PLFS statistics with NCS descriptions. Produces `data/processed/occupations_base.json`.

### Step 4: Score with Claude Haiku

```bash
# Add your key to .env first
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

python pipeline/4_score.py
```

Calls Claude Haiku for each occupation. Has checkpoint/resume support, so it can be interrupted and restarted. Cost is approximately $2 to $5 for 150 occupations.

### Step 5: Compile frontend data

```bash
python pipeline/5_compile.py
```

Produces `data/occupations.json` and `data/occupations.js`. The `.js` file wraps the JSON as `window.JOBS_DATA = {...}` so the frontend works on `file://` without a server.

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
| Treemap | D3 treemap (squarify, power-scaled employment) |
| Info card | D3 SVG radar chart, CSS glassmorphism |
| Data | Hardcoded JSON, loaded as JS global for file:// compat |
| Scoring | Python 3.10+, Anthropic SDK, Claude Haiku |
| Hosting | GitHub Pages |

---

## Data limitations

- **PLFS sample size**: some NCO 3-digit codes have small sample sizes at state level. National-level estimates are more reliable than state or district breakdowns.
- **Informal sector wages**: PLFS captures wages for regular wage and salaried workers reliably. Self-employed and casual worker incomes are harder to measure and may be underestimated.
- **Gig workers**: Platform workers like Swiggy and Ola drivers are classified under delivery and transport NCOs in PLFS. Dedicated gig economy counts come from NITI Aayog estimates, which are projections, not survey enumeration.
- **Agriculture**: 43 percent of India's workforce is in agriculture but PLFS wage data for subsistence farmers is limited. Many agricultural workers report zero or near-zero measured wages.
- **Data lag**: The most recent PLFS at time of build was 2023-24. India targets annual PLFS releases but delays of 12 to 18 months are common. The pipeline can be re-run when new data is available.

---

## Acknowledgements

- [Andrej Karpathy](https://karpathy.ai/jobs/) for the original US jobs visualisation concept and scoring prompt structure
- MoSPI (Ministry of Statistics and Programme Implementation) for PLFS microdata
- NASSCOM for IT sector employment estimates
- National Career Service (NCS) portal for occupation descriptions

---

## License

MIT. The compiled data files in `data/` are derived from publicly available government publications (PLFS, QES, NASSCOM). See individual source links above for their terms.
