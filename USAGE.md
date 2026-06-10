# Usage

How to use, share, embed and build on Indian Jobs Map.

## Just viewing it

Open the live site: [konkomaji.github.io/indianjobsmap](https://konkomaji.github.io/indianjobsmap)

- Each rectangle is one occupation. Bigger rectangle means more workers.
- Use the **Colour by** chips to switch what the colours mean: AI Exposure, Automation Risk, Median Wage, Formalization, Gig Potential, Growth.
- Hover (on desktop) or tap (on mobile) any occupation to see its details: worker count, median wage, rural and informal share, a radar chart of its scores, an India-specific note, and the AI scoring rationale.
- The colour scale for the active layer sits right under the chips.

## Running it locally

No installation or build step.

```bash
git clone https://github.com/konkomaji/indianjobsmap.git
cd indianjobsmap
```

Then either double-click `index.html`, or serve it:

```bash
python -m http.server 8000
# visit http://localhost:8000
```

The data loads from `data/occupations.js` (set as `window.JOBS_DATA`), so it works even when opened directly from disk.

## Using the data

The compiled dataset is `data/occupations.json`. Structure:

```json
{
  "meta": { "title": "...", "total_workers": 616000000, "source_primary": "...", "method": "..." },
  "major_groups": { "1": "Managers", "...": "..." },
  "occupations": [
    {
      "code": "251",
      "name": "Software & Applications Developers",
      "major_group": "2",
      "employment": 4000000,
      "median_wage": 540000,
      "rural_pct": 11,
      "informal_pct": 2,
      "ai_exposure": 9,
      "ai_rationale": "...",
      "automation_risk": 3,
      "formalization_potential": 6,
      "gig_potential": 4,
      "growth_outlook": "fast-growing",
      "india_note": "..."
    }
  ]
}
```

You may use this aggregated data in your own work. Please credit Indian Jobs Map and note that the figures are derived from PLFS 2025 microdata published by NSO/MoSPI. See LICENSE for terms. Do not present the AI-exposure scores as official statistics; they are estimates.

## Embedding

The site is a single static page. To embed it in another page, use an iframe:

```html
<iframe src="https://konkomaji.github.io/indianjobsmap"
        style="width:100%;height:80vh;border:0;border-radius:16px"
        title="Indian Jobs Map"></iframe>
```

## Regenerating the data

If you want to rebuild from the source microdata (for a new PLFS round, or to change the scoring), follow the pipeline steps in the README under "How the PLFS 2025 microdata was processed". In short:

```bash
# after placing CPERV1.txt in data/raw/plfs/
python pipeline/6_parse_plfs2025.py --apply
python pipeline/5b_compile_2025.py
```

## What you should not do

- Do not present the scores as government data. They are estimates on an anchored scale.
- Do not redistribute PLFS unit-level microdata. Only the aggregated occupation figures are shared here, in line with MoSPI's terms.
- Do not claim this is a forecast of job losses. AI exposure measures how much AI can reshape the work, not whether the job disappears.

## Credit

Built by [Konko Maji](https://www.linkedin.com/in/konkomaji/). Inspired by [karpathy/jobs](https://karpathy.ai/jobs/). Data from NSO/MoSPI PLFS 2025.
