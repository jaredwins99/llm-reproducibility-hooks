You are a translator between registers. Render the DEMAND below into the LEXIS specified, producing a prompt that will be given verbatim to another model.

DEMAND (semantic content to preserve as far as the lexis allows — do not add or remove considerations, do not tilt it toward any answer):
{demand}

LEXIS SPECIFICATION:
{lexis_json}

The lexis is a BOUNDED repertoire. Translation rules:
- Use ONLY vocabulary and constructions inside the repertoire. Respect vocabulary_out, the abstraction ceiling, the hedging norms, and the syntax limits absolutely.
- Where the demand contains concepts the lexis cannot express, do what a real speaker of this register would do: simplify, concretize, or approximate with the limited means available. The translation SHOULD be lossy where the repertoire forces it. Do not smuggle in out-of-repertoire words to preserve precision.
- The demand's neutrality must survive: if the original doesn't argue a side, neither may your rendering.

Produce the translated prompt with this structure:
1. An opening that establishes the voice: 3-5 example utterances adapted from the lexis spec so the reader is primed in the register. These examples must have NOTHING to do with the demand's topic — everyday matters only (weather, work, tools, food, family). Any topical content in the examples would prime a stance, not just a register. The reader will NEVER be told the rules of this register — your examples are the ONLY thing teaching them how to talk. Make them carry the register fully: its rhythm, its plainness or its elaboration, its silences.
2. The demand itself, rendered strictly within the lexis — the topic gets whatever expression the repertoire allows it, nothing more.
3. At most a brief in-register nudge to answer in the same way of talking (e.g., "talk plain like this"). Do NOT list rules, do NOT name forbidden words, do NOT describe the register — stating the bounds would step outside the lexis. The reader follows suit from your examples, nothing else.
4. This exact answer instruction, appended VERBATIM as the final line (do not translate or alter it):
{answer_instruction}

Output a single JSON object, nothing else:
{
  "translated_prompt": "<the full text to give the respondent>"
}
