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
1. An opening that establishes the voice: 2-3 example utterances adapted from the lexis spec (topic-neutral) so the reader is primed in the register.
2. The demand itself, rendered strictly within the lexis.
3. An instruction, phrased inside the lexis, telling the reader to answer in this same way of talking — using only this kind of language, not switching into fancier or more technical words than this register has.
4. This exact answer instruction, appended VERBATIM as the final line (do not translate or alter it):
{answer_instruction}

Output a single JSON object, nothing else:
{
  "translated_prompt": "<the full text to give the respondent>"
}
