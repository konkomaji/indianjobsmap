# Contributing to Indian Jobs Map

Thank you for your interest. This project aims to be the most complete, India-specific picture of who works at what in India, and it is built to grow. Contributions of every size are welcome, from fixing a typo in an occupation note to adding an entire new data layer.

You do not need to be an expert. If you are an economist, a data person, a designer, a developer, a student, or simply someone who knows a trade well and can improve an occupation's description, there is room for you here.

## Ways to contribute

- **Improve occupation notes**: each occupation has a short plain-English India note. If you know a trade better, make it more accurate.
- **Refine the scores**: AI exposure, automation, formalization, gig potential and growth are estimates. Well-reasoned adjustments with a short justification are welcome.
- **Add data layers**: education level, unemployment, gender split, rural/urban, state-level views. The PLFS microdata already holds most of these fields.
- **Design and accessibility**: improve the Material 3 interface, mobile experience, colour contrast, or screen-reader support.
- **Vernacular labels**: add Hindi or other Indian-language names for occupations.
- **Bug fixes and performance**: anything that makes the tool more correct or faster.
- **Documentation**: clearer explanations help everyone.

## Project structure

```
index.html              The page (header, description, controls, treemap, legend)
style.css               Material 3 Expressive styling, saffron seed colour
app.js                  D3 treemap, layers, radar chart, info card, mobile sheet
data/occupations.json   Compiled dataset (118 occupations)
data/occupations.js     Same data as window.JOBS_DATA (for file:// and Pages)
pipeline/               Scripts that build the dataset from PLFS microdata
  6_parse_plfs2025.py   Parse CPERV1.txt unit-level microdata
  scores_2025.py        AI exposure + India scores per occupation
  5b_compile_2025.py    Merge stats + scores into occupations.json/.js
```

See the README for the full data-processing method.

## Setup

No build step. To run locally:

```bash
git clone https://github.com/konkomaji/indianjobsmap.git
cd indianjobsmap

# open index.html directly, or serve it:
python -m http.server 8000
# then visit http://localhost:8000
```

To regenerate the dataset you need the PLFS 2025 microdata (see README, "How the PLFS 2025 microdata was processed"). The raw microdata is not in the repo because of MoSPI's terms; only the compiled output is committed.

## Making a change

1. Fork the repository and create a branch: `git checkout -b my-change`.
2. Make your change. Keep the style of the surrounding code.
3. If you change occupation data, edit the pipeline source (`scores_2025.py` for scores and notes), then re-run `python pipeline/5b_compile_2025.py` so `occupations.json` and `occupations.js` stay in sync. Do not hand-edit the compiled JSON.
4. Test by opening the page locally and checking the treemap renders and the info card works.
5. Commit with a clear message describing what and why.
6. Open a pull request against `main` with a short description.

## Writing style

- Indian English, plain and human. Write for an ordinary Indian reader, not an economist.
- No em-dashes. Use commas, full stops, or rephrase.
- Occupation notes should say what the job actually is in India, with a concrete fact where possible (a scheme name, a company, a number).

## Data and scoring principles

- Employment, wages, rural share and informality come only from the PLFS microdata, never invented.
- Do not scale or fabricate numbers to fit a story. If data is missing, say so.
- AI exposure follows the Karpathy-style anchored 0 to 10 scale in the README, adapted for India. A high score means AI can reshape the work, not that the job will disappear.

## Code of conduct

Be respectful and constructive. This is a public-good project for India. Assume good faith, help newcomers, and keep discussion focused on the work.

## Questions

Open an issue on GitHub, or reach the maintainer, [Konko Maji](https://www.linkedin.com/in/konkomaji/).
