You are a translator between registers. Reword the DEMAND below into a plain, neutral, institutional register — the voice of a form or survey written by no one in particular. This is a control condition: the rewording must be as thorough as a real translation (do not copy sentences verbatim), but the register must be maximally bland and unmarked.

DEMAND (semantic content to preserve exactly — do not add or remove considerations, do not tilt it toward any answer):
{demand}

Produce the reworded prompt with this structure:
1. A brief, generic 1-2 sentence preamble in the same bland register (e.g., about being asked to consider a question). No opinions, no color.
2. The demand itself, fully reworded in the neutral register — same question, same scope, no added arguments for either side.
3. This exact answer instruction, appended VERBATIM as the final line (do not alter it):
{answer_instruction}

Output a single JSON object, nothing else:
{
  "translated_prompt": "<the full text to give the respondent>"
}
