You are a translator between registers. Reword the DEMAND below into a plain, neutral, institutional register — the voice of a form or survey written by no one in particular. This is a control condition: the rewording must be as thorough as a real translation (do not copy sentences verbatim), but the register must be maximally bland and unmarked.

DEMAND (its truth conditions are pinned below — your rewording must ask EXACTLY this question):
{demand}

TRUTH CONDITIONS (a checker will verify your rewording against these):
{truth_conditions}

Rules:
- SEMANTIC FIDELITY IS ABSOLUTE. Preserve the modal meaning, the decision rule, the scope, and the comparison exactly. Do not shift modal strength (e.g., "should" must not become "advisable" if the truth conditions define it otherwise), do not change thresholds, do not add or remove considerations, examples, or intensifiers.
- Before output, self-check your rewording against each line of the truth conditions.

Produce the reworded prompt with this structure:
1. A brief, generic 1-2 sentence preamble in the same bland register (e.g., about being asked to consider a question). No opinions, no color, no topical content.
2. The demand itself, fully reworded in the neutral register and strictly within the truth conditions.
3. This exact answer instruction, appended VERBATIM as the final line (do not alter it):
{answer_instruction}

Output a single JSON object, nothing else:
{
  "translated_prompt": "<the full text to give the respondent>"
}
