---
name: repo-to-fundraising-pitchdeck
description: Convert a side project, hackathon prototype, or software repository into an investor-ready pre-seed fundraising pitch deck using Slidev and Borys Musielak's 8-slide framework. Use when a user asks to turn repo code into a fundraising narrative, create a VC pitch deck, or produce/export pitch slides as Slidev/PDF/PPTX.
---

# Repo To Fundraising Pitch Deck

Turn repository facts into a concise investor narrative and render it as a Slidev deck.

## Required References

Read before generating deck content:
- `references/pitch-framework-borys-musielak.md`
- `references/slidev-playbook.md`
- `references/brief-template.json`

## Workflow

1. Extract repository evidence
- Read `README*`, docs, manifests (`package.json`, `pyproject.toml`, `go.mod`, etc.), demos, and recent commit history.
- Split findings into `verified` facts and `assumptions` that need founder confirmation.
- Do not invent users, revenue, growth, or market numbers.

2. Build the fundraising brief
- Fill the schema in `references/brief-template.json`.
- Keep each section to one core claim and up to 3-5 bullets.
- Add evidence or assumption notes for every slide section.

3. Generate the Slidev draft
- Run this helper from the skill directory:
```bash
python3 scripts/generate_slidev_pitchdeck.py \
  --brief references/brief-template.json \
  --out slides.md \
  --repo-path .
```
- Replace `references/brief-template.json` with your real brief path.
- Keep auto-generated repository signals on the traction slide unless clearly irrelevant.

4. Polish for investor readability
- Keep one idea per slide.
- Use click reveals only for progressive disclosure (`<v-clicks>`), never as decoration.
- Prefer built-in layouts and consistent formatting over custom visual complexity.
- Add presenter notes that mark assumptions and cite evidence.

5. Validate and export
- Run `slidev slides.md` to review.
- Run `slidev export --format pdf` for investor sharing.
- Run `slidev export --format pptx` only when explicitly requested.

## Output Contract

- Produce `slides.md` with exactly eight fundraising slides:
  1. Company + one-line pitch
  2. Team
  3. Problem
  4. Solution
  5. Why now
  6. Traction
  7. Market
  8. Ask
- Include slide notes with `Evidence` and `Assumptions to confirm` whenever data is uncertain.
- Keep the ask explicit: amount, runway, and milestone plan.

## Guardrails

- Optimize for clarity, narrative, founder conviction, and momentum.
- Prefer concrete proof from repo artifacts over abstract claims.
- If evidence is thin, explicitly call out the gap and propose minimum validation experiments.
