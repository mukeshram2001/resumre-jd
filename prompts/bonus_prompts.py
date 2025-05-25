def get_buzzword_analysis_prompt(resume_text: str, jd_text: str) -> str:
    """
    Generates a prompt to identify irrelevant or potentially negative buzzwords in a resume
    in the context of a given job description.
    Requests JSON output: [{"buzzword": "word", "reasoning": "explanation"}]
    """
    return f"""
Analyze the following resume text for buzzwords or jargon that might be considered irrelevant, overused, or potentially counterproductive when compared against the provided job description.
Focus on terms that don't add substantial value or might be perceived negatively by a recruiter for this specific role.

Resume Text:
---
{resume_text}
---

Job Description Text:
---
{jd_text}
---

Provide your response as a JSON list of objects. Each object should have two keys:
1.  "buzzword": The identified buzzword or phrase from the resume.
2.  "reasoning": A brief explanation of why this term might be problematic for this specific JD (e.g., "Overused corporate jargon, lacks specificity for a technical role," or "This term is more relevant to marketing, while the JD is for an engineering position.").

If no such buzzwords are identified, return an empty list.

Example JSON output:
[
  {{"buzzword": "Results-oriented", "reasoning": "This is a common filler phrase. It's better to demonstrate results with specific achievements and metrics rather than stating this directly."}},
  {{"buzzword": "Synergistic innovator", "reasoning": "Sounds like jargon without concrete meaning. Focus on specific innovative projects or collaborative achievements."}}
]
"""
