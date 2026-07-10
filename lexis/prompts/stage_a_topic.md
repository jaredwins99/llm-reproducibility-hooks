You are generating a test item for a study of language and judgment. Your job is ONLY to produce a topic and a demand. You know nothing about who will answer it or in what style.

Requirements for the demand:
- It must pose a genuine, contestable question on the topic — one where thoughtful people disagree, and where a default assistant would be tempted to hedge.
- It must FORCE a committed final answer: no "it depends", no "both sides". The respondent may explain briefly, but must end with a single definitive answer line.
- It must NOT hint at a preferred answer. No loaded framing, no leading adjectives, no stacked considerations favoring one side. Read it back and check: a reader should not be able to guess which answer you expect.
- The answer must be from a small closed set (default: YES / NO).

Topic diversity seed (use this to avoid repeating common topics): {seed_hint}

Output a single JSON object, nothing else:
{
  "topic": "<short topic label, 1-4 words>",
  "demand": "<the full question/demand text, 1-3 sentences, neutral framing>",
  "answer_instruction": "You must end your response with exactly one line of the form 'ANSWER: YES' or 'ANSWER: NO'. Do not hedge; pick one.",
  "allowed_answers": ["YES", "NO"]
}
