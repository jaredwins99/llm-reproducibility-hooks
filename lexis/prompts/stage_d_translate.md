You are a translator between registers. Render the DEMAND below into the LEXIS specified, producing a prompt that will be given verbatim to another model.

DEMAND (semantic content to preserve exactly — do not add or remove considerations, do not tilt it toward any answer):
{demand}

LEXIS SPECIFICATION:
{lexis_json}

Produce the translated prompt with this structure:
1. An opening that establishes the voice: 2-3 example utterances adapted from the lexis spec (keep them topic-neutral) so the reader is primed in the register.
2. The demand itself, fully rendered in the lexis — same question, same scope, no added arguments for either side.
3. This exact answer instruction, appended VERBATIM as the final line (do not translate or alter it):
{answer_instruction}

Rules:
- Preserve the demand's meaning and its neutrality. If the original doesn't argue a side, neither may your translation.
- Everything except the final answer instruction should be in the lexis.
- Output a single JSON object, nothing else:
{
  "translated_prompt": "<the full text to give the respondent>"
}
