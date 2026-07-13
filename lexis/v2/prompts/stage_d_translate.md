You are a translator between registers. Render the DEMAND below into the LEXIS specified, producing a prompt that will be given verbatim to another model.

DEMAND (its truth conditions are pinned below — your rendering must ask EXACTLY this question):
{demand}

TRUTH CONDITIONS (a checker will verify your rendering against these):
{truth_conditions}

LEXIS SPECIFICATION:
{lexis_json}

The lexis is a BOUNDED repertoire. Translation rules:
- Use ONLY vocabulary and constructions inside the repertoire. Respect vocabulary_out, the abstraction ceiling, the hedging norms, and the syntax limits absolutely.
- SEMANTIC FIDELITY IS ABSOLUTE. Your rendering must preserve: the modal meaning, the decision rule, the scope, and the comparison — exactly as pinned in the truth conditions. Where the register lacks a word, rebuild the SAME meaning from simpler or different words; never a stronger meaning, never a weaker one, never a different question.
- Spend the register on FORM ONLY: vocabulary, syntax, cadence, hedging markers. Do NOT add content: no considerations, no arguments, no pro/con framing, no examples about the topic, no intensifiers (e.g., do not add "forever", "always", "not ever" unless the demand itself says so). Even if this register normally elaborates (enumerating considerations, steelmanning), DO NOT do so for the demand — render the bare question and stop.
- Before output, self-check your rendering against each line of the truth conditions: same modal? same decision rule? same scope? same comparison? nothing added, nothing dropped?

Produce the translated prompt with this structure:
1. An opening that establishes the voice: 3-5 example utterances adapted from the lexis spec so the reader is primed in the register. These examples must have NOTHING to do with the demand's topic — everyday matters only (weather, work, tools, food, family). Any topical content in the examples would prime a stance, not just a register. The reader will NEVER be told the rules of this register — your examples are the ONLY thing teaching them how to talk. Make them carry the register fully: its rhythm, its plainness or its elaboration, its silences.
2. The demand itself, rendered strictly within the lexis AND strictly within the truth conditions.
3. At most a brief in-register nudge to answer in the same way of talking (e.g., "talk plain like this"). Do NOT list rules, do NOT name forbidden words, do NOT describe the register — stating the bounds would step outside the lexis. The reader follows suit from your examples, nothing else.
4. This exact answer instruction, appended VERBATIM as the final line (do not translate or alter it):
{answer_instruction}

Output a single JSON object, nothing else:
{
  "translated_prompt": "<the full text to give the respondent>"
}
