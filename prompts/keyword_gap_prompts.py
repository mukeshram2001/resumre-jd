def get_missing_keywords_prompt(resume_text: str, jd_text: str) -> str:
    """
    Returns the prompt for identifying missing keywords in the resume compared to the JD.
    Requests a JSON output.
    """
    return f"""
Analyze the provided resume and job description. Identify keywords from the job description that are crucial for the role but are missing or not adequately represented in the resume.
Also, provide a summary of relevant keywords found in the resume and their frequencies.

Provide your response in JSON format with the following structure:
{{
  "missing_keywords": ["<list of strings, keywords from JD missing in resume>"],
  "resume_keywords_summary": {{ "<keyword_from_resume>": <frequency_integer> }}
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""

def get_role_mismatch_prompt(resume_text: str, jd_text: str) -> str:
    """
    Returns the prompt for identifying potential role mismatches, experience gaps, and qualification gaps.
    Requests a JSON output containing lists of RoleMismatchSignal objects.
    """
    return f"""
Analyze the provided resume and job description to identify:
1.  Significant experience gaps (e.g., missing years in specific domains, lack of project types required by JD).
2.  Gaps in formal qualifications (e.g., required certifications, degrees).
3.  Potential role mismatches (e.g., overqualified, underqualified, different career trajectory). For each mismatch, provide a signal type, reasoning, and supporting evidence from the texts.

Provide your response in JSON format with the following structure:
{{
  "experience_gaps": ["<list of strings, identified experience gaps>"],
  "qualification_gaps": ["<list of strings, identified qualification gaps>"],
  "potential_mismatches": [
    {{
      "signal_type": "<string, e.g., 'Overqualified', 'Underqualified', 'Different Career Trajectory'>",
      "reasoning": "<string, explanation for the signal>",
      "evidence": ["<list of strings, specific phrases or facts from resume/JD supporting this signal>"]
    }}
  ]
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""
