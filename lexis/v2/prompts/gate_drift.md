You are a semantic-equivalence checker. Below is an ORIGINAL question with pinned truth conditions, and a RENDERING of that question in a different linguistic register. Verify that the rendering asks EXACTLY the same question.

ORIGINAL DEMAND:
{demand}

TRUTH CONDITIONS:
{truth_conditions}

RENDERING (register differences are expected and fine — only SEMANTIC deviations matter):
{rendering}

Check, one by one:
1. MODAL: same modal meaning as pinned (e.g., better-on-balance vs obligatory vs advisable)?
2. DECISION RULE: same threshold for YES vs NO?
3. SCOPE: same who/where/when?
4. COMPARISON: same alternative being compared against?
5. ADDED CONTENT: does the rendering add considerations, arguments, pro/con framing, examples about the topic, or intensifiers (e.g., "forever", "never", "always") absent from the original?
6. DROPPED CONTENT: does the rendering drop any restriction or qualifier that changes what is being asked?

Judge register-driven simplification charitably: rebuilding a concept from simpler words is fine IF the meaning survives. Flag it only when the meaning shifts (stronger, weaker, or different).

Output a single JSON object, nothing else:
{
  "equivalent": true or false,
  "violations": ["<one short line per violation, naming the check number and the exact offending text>"]
}
