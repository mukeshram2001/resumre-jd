from typing import List, Optional

def get_rewrite_headline_prompt(original_headline: str, jd_keywords: List[str], target_role_title: Optional[str]) -> str:
    """
    Generates a prompt to rewrite a resume headline.
    Requests JSON output: {"rewritten_headline": "new headline text", "attempted_keywords": ["kw1", "kw2"]}
    """
    keywords_str = ", ".join(jd_keywords)
    role_focus = f"The target role is '{target_role_title}'." if target_role_title else "The target role is not specified, focus on general professional appeal."

    return f"""
Please rewrite the following resume headline to be more impactful and to incorporate relevant keywords.
{role_focus}

Original Headline:
"{original_headline}"

Job Description Keywords to consider:
{keywords_str}

Output the result in JSON format with two keys: "rewritten_headline" (string) and "attempted_keywords" (list of strings, keywords you tried to include).
Strive for a concise and professional headline.

Example JSON output:
{{
  "rewritten_headline": "Senior Software Engineer | Python, AWS, Agile | AI Enthusiast",
  "attempted_keywords": ["Senior Software Engineer", "Python", "AWS", "AI"]
}}
"""

def get_rewrite_summary_prompt(
    original_summary: str,
    jd_keywords: List[str],
    missing_keywords_from_resume: List[str],
    key_jd_requirements: List[str]
) -> str:
    """
    Generates a prompt to rewrite a resume summary/objective.
    Requests JSON output: {"rewritten_summary": "new summary text", "attempted_keywords": ["kw1", "kw2"]}
    """
    jd_keywords_str = ", ".join(jd_keywords)
    missing_keywords_str = ", ".join(missing_keywords_from_resume)
    key_requirements_str = "\n- ".join(key_jd_requirements)

    return f"""
Please rewrite the following resume summary/objective. The goal is to make it more compelling, align it better with the key job description requirements, and incorporate relevant keywords, especially those missing from the resume.

Original Summary/Objective:
"{original_summary}"

Keywords from Job Description to consider:
{jd_keywords_str}

Keywords currently MISSING from the resume that are important for the JD:
{missing_keywords_str}

Key Job Description Requirements to address:
- {key_requirements_str}

Output the result in JSON format with two keys: "rewritten_summary" (string) and "attempted_keywords" (list of strings, keywords you tried to include from any of the provided lists).
Focus on creating a concise, impactful summary (3-4 sentences) that highlights the candidate's suitability for a role with these requirements.

Example JSON output:
{{
  "rewritten_summary": "Results-driven Senior Software Engineer with 8+ years of experience in Python, AWS, and leading agile teams. Proven ability to deliver scalable solutions and passionate about leveraging AI/ML for innovative products. Successfully integrated CI/CD pipelines for multiple projects.",
  "attempted_keywords": ["Senior Software Engineer", "Python", "AWS", "agile", "AI/ML", "CI/CD"]
}}
"""

def get_rewrite_experience_bullets_prompt(
    original_bullets: List[str],
    company_name: str,
    role_title: str,
    jd_keywords: List[str],
    missing_keywords_from_resume: List[str]
) -> str:
    """
    Generates a prompt to rewrite work experience bullet points.
    Requests JSON output: {"rewritten_bullets": ["bullet1", "bullet2"], "attempted_keywords": ["kw1", "kw2"]}
    """
    original_bullets_str = "\n".join([f"- {bullet}" for bullet in original_bullets])
    jd_keywords_str = ", ".join(jd_keywords)
    missing_keywords_str = ", ".join(missing_keywords_from_resume)

    return f"""
Please rewrite the following work experience bullet points for the role of '{role_title}' at '{company_name}'.
The goal is to make them more achievement-oriented (quantify where possible), incorporate relevant job description keywords, and address any missing keywords.

Original Bullet Points:
{original_bullets_str}

Keywords from Job Description to consider for incorporation:
{jd_keywords_str}

Keywords currently MISSING from the resume that are important for the JD (try to weave these in if relevant to the experience):
{missing_keywords_str}

Output the result in JSON format with two keys: "rewritten_bullets" (list of strings) and "attempted_keywords" (list of strings, keywords you tried to include from any of the provided lists).
Ensure each bullet point starts with a strong action verb. Maintain the original number of bullet points.

Example JSON output:
{{
  "rewritten_bullets": [
    "Led a team of 5 engineers to develop and launch a new SaaS platform using Python and AWS, resulting in a 20% increase in user engagement.",
    "Engineered scalable microservices with Docker and Kubernetes, improving system reliability by 15%.",
    "Implemented CI/CD pipelines with Jenkins, reducing deployment times by 30%."
  ],
  "attempted_keywords": ["Python", "AWS", "SaaS", "Docker", "Kubernetes", "CI/CD", "Jenkins", "Led", "Engineered"]
}}
"""
