from typing import List, Optional

def get_ats_rejection_predictor_prompt(resume_text: str, jd_hard_constraints: List[str]) -> str:
    """
    Generates a prompt for the Gemini API to predict ATS rejection based on hard constraints.
    Requests JSON output detailing the verdict, reason, and status of each checked criterion.
    Handles the case where jd_hard_constraints is empty.
    """
    if not jd_hard_constraints:
        return f"""
Analyze the provided resume. Since no specific hard constraints from the job description were provided,
assess general ATS compatibility and flag any obvious issues that might lead to rejection by a generic ATS.
For example, issues with parsing, lack of standard sections (like contact info, experience, education), or highly unusual formatting.

Provide your response in JSON format with the following structure:
{{
  "overall_verdict": "<string, 'Manual Review Needed' or 'Likely Pass (No Hard Constraints Provided)'>",
  "overall_reason": "<string, explanation focusing on general ATS compatibility or lack of specific constraints to check against>",
  "checked_criteria": [
    {{
      "criterion_description": "<string, e.g., 'Standard Resume Sections Present', 'Parsable Format'>",
      "status": "<string, 'Met', 'Not Met', 'Unclear from Resume'>",
      "reasoning": "<string, optional: if not met or unclear>"
    }}
  ]
}}

Resume:
{resume_text}

Example for no hard constraints:
{{
  "overall_verdict": "Manual Review Needed",
  "overall_reason": "No hard constraints provided by JD. Resume appears to have standard sections and parsable format, but cannot check against specific knockout criteria.",
  "checked_criteria": [
    {{"criterion_description": "Presence of Contact Information", "status": "Met", "reasoning": null}},
    {{"criterion_description": "Presence of Experience Section", "status": "Met", "reasoning": null}},
    {{"criterion_description": "Presence of Education Section", "status": "Met", "reasoning": null}},
    {{"criterion_description": "Overall Readability/Parsability", "status": "Met", "reasoning": "Uses standard fonts and layout."}}
  ]
}}
"""

    constraints_list_str = "\n".join([f"- {constraint}" for constraint in jd_hard_constraints])

    return f"""
Analyze the provided resume against the following hard constraints extracted from a job description.
Determine if an Applicant Tracking System (ATS) would likely auto-reject the candidate based *only* on these explicit criteria.
For each criterion, state if it's 'Met', 'Not Met', or 'Unclear from Resume'. Provide reasoning for 'Not Met' or 'Unclear'.

Hard Constraints from Job Description:
{constraints_list_str}

Resume:
{resume_text}

Provide your response in JSON format with the following structure:
{{
  "overall_verdict": "<string, 'Likely Pass', 'Likely Reject', 'Manual Review Needed'>",
  "overall_reason": "<string, brief overall reasoning for the verdict based on the hard constraints>",
  "checked_criteria": [
    {{
      "criterion_description": "<string, the exact hard constraint checked>",
      "status": "<string, 'Met', 'Not Met', 'Unclear from Resume'>",
      "reasoning": "<string, optional: if not met or unclear, explain why>"
    }}
  ]
}}

Example:
{{
  "overall_verdict": "Likely Reject",
  "overall_reason": "Fails to meet the mandatory 'PMP Certification' requirement.",
  "checked_criteria": [
    {{"criterion_description": "Must have a Bachelor's degree in Engineering", "status": "Met", "reasoning": null}},
    {{"criterion_description": "Must have PMP Certification", "status": "Not Met", "reasoning": "PMP Certification not found in resume."}},
    {{"criterion_description": "Minimum 5 years of project management experience", "status": "Met", "reasoning": null}}
  ]
}}
Focus strictly on the provided hard constraints. Do not infer or evaluate other aspects of the resume.
"""
