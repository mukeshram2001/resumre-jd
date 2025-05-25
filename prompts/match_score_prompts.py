def get_hard_skills_prompt(resume_text: str, jd_text: str) -> str:
    """Returns the prompt for evaluating hard skills match."""
    return f"""
Analyze the following resume and job description to assess the match in hard skills.
Provide your response in JSON format with the following structure:
{{
  "score": <float, 0-100, representing the percentage of hard skills matched>,
  "rationale": "<string, explaining the basis of the score>",
  "matched_skills": ["<list of strings, matched hard skills>"],
  "missing_skills": ["<list of strings, hard skills present in JD but missing in resume>"]
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""

def get_soft_skills_prompt(resume_text: str, jd_text: str) -> str:
    """Returns the prompt for evaluating soft skills match."""
    return f"""
Analyze the following resume and job description to assess the match in soft skills.
Provide your response in JSON format with the following structure:
{{
  "score": <float, 0-100, representing the strength of soft skills demonstrated relevant to the JD>,
  "rationale": "<string, explaining the basis of the score>",
  "demonstrated_skills": ["<list of strings, soft skills demonstrated in the resume>"],
  "missing_skills": ["<list of strings, soft skills desired in JD but not evident in resume>"]
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""

def get_role_alignment_prompt(resume_text: str, jd_text: str) -> str:
    """Returns the prompt for evaluating role alignment."""
    return f"""
Analyze the resume against the job description to evaluate how well the candidate's experience, responsibilities, and career progression align with the requirements and expectations of the role.
Provide your response in JSON format with the following structure:
{{
  "score": <float, 0-100, assessing the alignment of the candidate's experience with the role>,
  "rationale": "<string, explaining the basis of the score, highlighting specific alignments or gaps>",
  "alignment_highlights": ["<list of strings, specific aspects of the resume that align well with the role>"],
  "alignment_gaps": ["<list of strings, aspects where the resume shows gaps in relation to the role requirements>"]
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""

def get_ats_compatibility_prompt(resume_text: str) -> str:
    """Returns the prompt for evaluating ATS compatibility."""
    return f"""
Analyze the following resume for its compatibility with Applicant Tracking Systems (ATS).
Consider factors like formatting, use of keywords, structure, and presence of elements that might be problematic for ATS parsing (e.g., images, tables, columns).
Provide your response in JSON format with the following structure:
{{
  "score": <float, 0-100, representing the resume's ATS compatibility>,
  "rationale": "<string, explaining the basis of the score, including specific formatting or content observations>",
  "suggestions_for_improvement": ["<list of strings, actionable suggestions to improve ATS compatibility>"],
  "problematic_elements": ["<list of strings, elements that might hinder ATS parsing>"]
}}

Resume:
{resume_text}
"""
