# Lexis Pilot 1 — Results (2026-07-13, FROZEN)

30 trials (5 topics × 6 roles), 3 arms, all stages `claude-sonnet-5` (audited via
JSON envelope). Results: `lexis/results/pilot1.jsonl` (90 rows). Trial transcripts:
`/home/godli/eval-work/lexis-pilot1/`. Prompts as of commit `7f4ee8b`.

## Headline numbers

- Lexis vs control flips: **8/29 (27.6%)**; neutral vs control: 3/29 (10.3%).
- McNemar exact (lexis-only=7 vs neutral-only=2 discordant): **p = 0.18** — underpowered.
- Required N for 80% power at observed rates: **~80 trials** (90%: ~106).
- Direction: 6/8 lexis flips were YES→NO; both NO→YES flips occurred on all-NO baseline topics.
- Control baselines fully deterministic per topic (YYYYYY or NNNNNN).
- 1 crashed E call, 1 unparseable answer (recorded as data).

## Flip matrix (lexis/neutral/control; * = lexis flip)

```
                          congestion  immigration  job-seeking  lab-meat  veganism
Basic-English speaker     Y/Y/Y       Y/Y/Y        Y/Y/Y        Y/N/N*    N/N/N
EA forum poster           Y/Y/Y       Y/Y/Y        Y/N/Y        N/N/N     Y/N/N*
elk hunter                Y/Y/Y       N/Y/Y*       N/Y/Y*       N/N/N     N/N/N
legal drafter             Y/Y/Y       N/Y/Y*       N/N/Y*       N/N/N     N/Y/N
southern revival preacher Y/Y/Y       N/Y/Y*       Y/Y/Y        N/N/N     N/N/N
texting teenager          Y/Y/Y       Y/?/Y        N/Y/Y*       N/N/N     N/N/N
```

## Findings beyond the numbers

1. **Register can reframe the question type**: EA×veganism flipped NO→YES with E
   explicitly reinterpreting "should" as normative-if-achieved rather than
   prescriptive-for-populations — and arguing *against* the anti-vegan
   considerations D had added. Flip attributable to frame, not smuggled stance.
2. **Semantic drift is pervasive and asymmetric**: D added considerations
   (EA cell: 4 numbered ones; Basic-English cell: a pro/con pair), added
   intensifiers ("every day, for their whole life, not ever"), and shifted modals
   ("should"→"advisable" — in the NEUTRAL arm) and thresholds ("substantial net
   waste"→"significant net loss"). Elaborated registers expand content;
   restricted registers force concretizations that add commitments.
3. **Ceiling effects**: deterministic baselines mean flips are only observable
   when a register pushes against the baseline direction (hunter×veganism could
   never show its expected effect).
4. **Counter to prediction**: immigration (most rehearsed) was most malleable
   (3/6 flips); congestion pricing never moved; EA didn't flip its home topic
   (lab meat for wildlife).

## Verdict

Effect direction is as hypothesized (register >> rewording), but pilot1 conflates
register effects with semantic drift. v2 must pin the demand's truth conditions
before the effect is interpretable.
