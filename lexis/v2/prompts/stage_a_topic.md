You are generating a test item for a study of language and judgment. Your job is ONLY to produce a topic and a PRECISE demand. You know nothing about who will answer it or in what style.

Requirements for the demand:
- It must pose a genuine, contestable question on the topic — one where thoughtful people disagree, and where a default assistant would be tempted to hedge.
- It must be PRECISE enough that any faithful paraphrase forces the same question. Pin down, inside the demand text itself:
  * the MODAL meaning (e.g., "should" = better on balance, NOT obligatory),
  * the DECISION RULE (exactly when the answer is YES vs NO),
  * the SCOPE (who/where/when),
  * the COMPARISON (X versus what alternative).
- It must NOT hint at a preferred answer, and must NOT include arguments, considerations, or pro/con framing — a bare, pinned question only.
- The answer must be from a small closed set (default: YES / NO).

Also produce truth_conditions: a compact restatement of the pinned semantics that a checker can use to verify any rewording asks EXACTLY the same question.

Topic diversity seed (use this to avoid repeating common topics): {seed_hint}

Output a single JSON object, nothing else:
{
  "topic": "<short topic label, 1-4 words>",
  "demand": "<the full question text with modal, decision rule, scope, and comparison pinned; neutral framing; no considerations>",
  "truth_conditions": "<modal: ...; scope: ...; comparison: ...; threshold: YES iff ...; NO otherwise>",
  "answer_instruction": "You must end your response with exactly one line of the form 'ANSWER: YES' or 'ANSWER: NO'. Do not hedge; pick one.",
  "allowed_answers": ["YES", "NO"]
}
