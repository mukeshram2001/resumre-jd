from typing import List, Optional

def get_cover_letter_prompt(
    candidate_name: Optional[str],
    top_strengths: List[str],
    jd_focus_areas: List[str],
    company_name: Optional[str],
    role_title: Optional[str]
) -> str:
    """
    Generates a prompt to create a concise and tailored cover letter.
    Requests JSON output for cover_letter_text and optional notes.
    """

    candidate_intro = f"The candidate's name is {candidate_name}." if candidate_name else "The candidate's name is not specified; use a generic placeholder if needed or omit."
    company_role_info = f"They are applying for the '{role_title if role_title else 'the position'}' at '{company_name if company_name else 'your company'}'."

    strengths_str = "\n- ".join(top_strengths) if top_strengths else "No specific strengths provided."
    focus_areas_str = "\n- ".join(jd_focus_areas) if jd_focus_areas else "No specific job description focus areas provided."

    return f"""
Please generate a concise and tailored cover letter based on the following candidate information and job description focus areas.
The cover letter should be professional, engaging, and highlight how the candidate's strengths align with the role.
It should be approximately 3-4 paragraphs long.

Candidate Information:
{candidate_intro}
{company_role_info}

Candidate's Key Strengths to Highlight:
- {strengths_str}

Job Description Focus Areas/Requirements to Address:
- {focus_areas_str}

Output the result in JSON format with two keys: "cover_letter_text" (string, the full text of the cover letter) and "notes" (optional string, any assumptions made or suggestions for further personalization).

Example JSON output:
{{
  "cover_letter_text": "Dear [Hiring Manager name or 'Hiring Team'],\\n\\nI am writing to express my enthusiastic interest in the {role_title if role_title else '[Role Title]'} position at {company_name if company_name else '[Company Name]'}. With my proven ability in [Strength 1] and experience in [Strength 2], I am confident I can significantly contribute to your team, particularly in areas such as [JD Focus Area 1] and [JD Focus Area 2].\\n\\nMy background in [briefly elaborate on a strength or relevant experience] has prepared me well to tackle the challenges of this role. I am particularly drawn to {company_name if company_name else 'your company'}'s work in [mention something specific if possible, otherwise general like 'innovation in the field'].\\n\\nI am eager to discuss how my skills in [Strength 3] and my proactive approach can benefit {company_name if company_name else 'your company'}. Thank you for your time and consideration.\\n\\nSincerely,\\n{candidate_name if candidate_name else '[Your Name]'}",
  "notes": "Consider adding a specific project example in the second paragraph if the candidate has one that strongly aligns with a JD focus area."
}}

Ensure the cover letter flows well and maintains a professional tone.
If candidate_name is not provided, use a placeholder like "[Your Name]".
If company_name or role_title are not provided, use placeholders like "[Company Name]" and "[Role Title]".
Address the letter to "Dear Hiring Team," if no specific hiring manager name is implied.
"""
