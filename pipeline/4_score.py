#!/usr/bin/env python3
"""
Score occupations using Claude Haiku on 5 dimensions:
  - ai_exposure (0-10)          — Karpathy-style anchored scale, India-adapted
  - automation_risk (0-10)
  - formalization_potential (0-10)
  - gig_potential (0-10)
  - growth_outlook (declining/stable/growing/fast-growing)

Input:  data/processed/occupations_base.json
Output: data/processed/occupations_scored.json

Requires: ANTHROPIC_API_KEY in .env
Cost:     ~$2-5 for 150 occupations with claude-haiku-4-5-20251001
"""

import anthropic
import json
import os
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

DATA = Path(__file__).parent.parent / "data" / "processed"
OUT = DATA / "occupations_scored.json"

SYSTEM = (
    "You are a labour economist specialising in India's workforce. "
    "You provide precise, evidence-based assessments of occupational trends in the Indian context. "
    "Return only valid JSON with no explanation or markdown."
)

# Karpathy-style scoring prompt, adapted for India
AI_EXPOSURE_SCALE = """
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
"""

PROMPT = AI_EXPOSURE_SCALE + """
Now also score these three additional dimensions and one qualitative outlook:

automation_risk (0-10): Physical automation likelihood (robots, machines) within 10 years in India.
India context: low labour costs delay automation vs the West by 5-10 years.
10 = highly repetitive structured tasks where machines are already cost-viable in India
0  = creative, relational, or highly variable physical work in unstructured environments

formalization_potential (0-10): Informal to formal employment transition likelihood in 5 years.
India context: GST, EPFO, UPI, e-Shram, PMKVY, gig platforms are the main drivers.
10 = rapidly formalising (platforms, organised retail, PMKVY-linked trades)
0  = permanently structural informal OR already fully formal

gig_potential (0-10): Can this occupation become platform or gig work via apps?
India context: Ola, Swiggy, Urban Company, NoBroker, Meesho are India's formalisation vector.
10 = born-platform (delivery, ride-hailing, home services, already happening at scale)
5  = partially platform-able (freelance, content, consulting)
0  = no gig path possible (government official, coal miner, subsistence farmer)

growth_outlook: Employment trajectory over the next 5 years.
One of exactly: "declining" | "stable" | "growing" | "fast-growing"

Occupation: {name}
NCO-2015 Code: {code}
Major Group: {major_group_name}
Total workers in India: {employment:,}
Median annual wage: Rs {median_wage:,}
Informal employment: {informal_pct}%
Rural workers: {rural_pct}%

Respond with ONLY a JSON object in this exact format, no other text:
{{"ai_exposure": <0-10>, "ai_rationale": "<2-3 sentences explaining the key factors in Indian context>", "automation_risk": <0-10>, "formalization_potential": <0-10>, "gig_potential": <0-10>, "growth_outlook": "<declining|stable|growing|fast-growing>"}}"""


def score_batch(client, occupations):
    """Score occupations one at a time with checkpoint/resume."""
    scored = []
    checkpoint = DATA / "occupations_scored_checkpoint.json"

    already_scored = {}
    if checkpoint.exists():
        for item in json.loads(checkpoint.read_text()):
            if "ai_exposure" in item:
                already_scored[item["code"]] = item

    for i, occ in enumerate(occupations):
        if occ["code"] in already_scored:
            print(f"  [{i+1}/{len(occupations)}] CACHED: {occ['name']}")
            scored.append(already_scored[occ["code"]])
            continue

        print(f"  [{i+1}/{len(occupations)}] Scoring: {occ['name']} (NCO {occ['code']})")

        for attempt in range(3):
            try:
                msg = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=400,
                    system=SYSTEM,
                    messages=[{
                        "role": "user",
                        "content": PROMPT.format(**occ)
                    }]
                )
                raw = msg.content[0].text.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                scores = json.loads(raw)
                scored.append({**occ, **scores})
                break
            except json.JSONDecodeError as e:
                print(f"    JSON error attempt {attempt+1}: {e}")
                if attempt == 2:
                    print(f"    SKIPPING -- using defaults")
                    scored.append({**occ, "ai_exposure": 3,
                                   "ai_rationale": "Score unavailable.",
                                   "automation_risk": 3,
                                   "formalization_potential": 3,
                                   "gig_potential": 3,
                                   "growth_outlook": "stable"})
            except Exception as e:
                print(f"    Error attempt {attempt+1}: {e}")
                time.sleep(2 ** attempt)
                if attempt == 2:
                    scored.append({**occ, "ai_exposure": 3,
                                   "ai_rationale": "Score unavailable.",
                                   "automation_risk": 3,
                                   "formalization_potential": 3,
                                   "gig_potential": 3,
                                   "growth_outlook": "stable"})

        if len(scored) % 10 == 0:
            checkpoint.write_text(json.dumps(scored, indent=2, ensure_ascii=False))

        time.sleep(0.3)

    return scored


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Add to .env file.")
        return

    base_path = DATA / "occupations_base.json"
    if not base_path.exists():
        print(f"Base data not found: {base_path}")
        print("Run 3_extract.py first.")
        return

    occupations = json.loads(base_path.read_text())
    print(f"Scoring {len(occupations)} occupations with claude-haiku-4-5-20251001...")
    print(f"Estimated cost: ~${len(occupations) * 0.025:.2f}")

    client = anthropic.Anthropic(api_key=api_key)
    scored = score_batch(client, occupations)

    OUT.write_text(json.dumps(scored, indent=2, ensure_ascii=False))
    print(f"\nScored {len(scored)} occupations -> {OUT}")

    ai_scores = [o["ai_exposure"] for o in scored if "ai_exposure" in o]
    if ai_scores:
        print(f"AI Exposure: avg={sum(ai_scores)/len(ai_scores):.1f}, "
              f"min={min(ai_scores)}, max={max(ai_scores)}")


if __name__ == "__main__":
    main()
