You are a descriptive sociolinguist. Develop a complete LEXIS specification for the following role — the bounded linguistic repertoire its speakers actually have.

Role: {role}
Register notes from a colleague: {register_notes}

A lexis is defined as much by what its speakers DON'T say as what they do. Simplified registers lack abstract vocabulary; restricted codes lack hedging constructions; some registers cap sentence complexity. Your specification must draw those boundaries explicitly.

You know NOTHING about what the lexis will be used to discuss. Keep every example topic-neutral (everyday matters: weather, work, tools, food, family). Do not mention any social or political issue.

Produce:
1. Vocabulary IN the repertoire: 10-15 characteristic words/phrases with glosses.
2. Vocabulary OUT of the repertoire: categories of words these speakers would not use (e.g., "abstract nouns like 'sustainability', 'tradeoff'", "Latinate formal verbs", "statistical qualifiers"), with 5-8 concrete examples of forbidden words.
3. Abstraction ceiling: 1-2 sentences on how abstract this register gets. What happens when a speaker hits a concept beyond it (circumlocution? concrete substitution? silence?).
4. Hedging norms: does this register hedge? What hedges exist in it, if any? (Some registers have essentially none.)
5. Syntax limits: max realistic sentence complexity, clause structure, tense range.
6. Example utterances: 5 short passages (1-3 sentences each) of everyday speech STRICTLY inside these bounds.

Output a single JSON object, nothing else:
{
  "role": "{role}",
  "vocabulary_in": [{"term": "...", "gloss": "..."}],
  "vocabulary_out": {"categories": ["..."], "forbidden_examples": ["..."]},
  "abstraction_ceiling": "...",
  "hedging_norms": "...",
  "syntax_limits": "...",
  "examples": ["...", "...", "...", "...", "..."]
}
