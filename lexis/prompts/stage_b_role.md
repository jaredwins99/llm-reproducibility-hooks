You are selecting a ROLE for a study of language and judgment. The role names a community or occupation with a distinctive way of speaking (a lexis: vocabulary, idioms, cadence, register).

The topic under discussion will be: {topic}

Requirements:
- Pick ONE role whose members have a recognizable, rich speech register — enough that text written in their voice is clearly identifiable.
- The role should have some real-world relationship to the topic (its members plausibly hold and express views about it), but do NOT state what that view is, and do NOT pick a role solely because its stance is obvious.
- Prefer specific over generic ("longline fisherman" over "worker").

Output a single JSON object, nothing else:
{
  "role": "<the role, 1-4 words>",
  "register_notes": "<2-3 sentences on what makes this community's speech distinctive: vocabulary domains, syntax habits, values expressed through language. Do NOT mention the topic.>"
}
