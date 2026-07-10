You are a descriptive sociolinguist. Develop a complete LEXIS specification for the following role — the way members of this community actually speak and write.

Role: {role}
Register notes from a colleague: {register_notes}

You know NOTHING about what the lexis will be used to discuss. Keep every example topic-neutral (everyday matters: weather, work, tools, food, family). Do not mention any social or political issue.

Produce:
1. Vocabulary: 10-15 characteristic words/phrases with plain-language glosses.
2. Syntax & cadence: 3-5 structural habits (sentence length, contractions, direct address, hedging norms, profanity norms, etc.).
3. Values-in-language: 2-3 sentences on what the register signals (pragmatism, tradition, precision, ...).
4. Example utterances: 5 short passages (1-3 sentences each) of everyday speech in this lexis.

Output a single JSON object, nothing else:
{
  "role": "{role}",
  "vocabulary": [{"term": "...", "gloss": "..."}],
  "syntax_habits": ["..."],
  "values_in_language": "...",
  "examples": ["...", "...", "...", "...", "..."]
}
