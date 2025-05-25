from typing import List, Dict, Any

def get_recruiter_lens_prompt(
    resume_text: str,
    jd_text: str,
    match_score_summary: Dict[str, Any],
    missing_keywords: List[str],
    role_mismatches: List[Dict[str, Any]] # Expects list of RoleMismatchSignal like dicts
) -> str:
    """
    Generates a prompt for simulating a recruiter's 7-second scan of a resume against a JD.
    Requests JSON output for positives, red flags, verdict, and reason.
    """

    # Formatting inputs for brevity and impact in the prompt
    formatted_score_summary = "\n".join([f"- {key.replace('_', ' ').title()}: {value['score']:.1f}/100" for key, value in match_score_summary.items() if key.endswith('_score')])
    
    mismatch_highlights = []
    if role_mismatches:
        for mismatch in role_mismatches[:2]: # Limit to first 2 mismatches for brevity
            mismatch_highlights.append(f"- {mismatch.get('signal_type', 'N/A')}: {mismatch.get('reasoning', 'N/A')[:100]}...") # Truncate reasoning
    else:
        mismatch_highlights.append("- No major mismatches identified from detailed analysis.")
    
    mismatches_str = "\n".join(mismatch_highlights)
    missing_keywords_str = ", ".join(missing_keywords[:5]) if missing_keywords else "None critical" # Limit to first 5 keywords
    top_skills_resume = "Python, Java, Agile, Microservices" # Placeholder - ideally extract from resume_text or summary
    key_jd_reqs = "Senior AI Engineer, Python, TensorFlow, Kubernetes, AI project leadership, MLOps" # Placeholder - ideally extract from jd_text

    return f"""
Simulate a recruiter's 7-second initial scan of the following resume against the key job description requirements.
Based on this quick review, identify key positives, red flags, and provide an initial verdict ('Proceed', 'Hold', 'Reject') with a brief justification.

Job Description Key Requirements:
{key_jd_reqs}

Resume Snippet (simulate quick scan focus on recent role, skills):
--- Resume Start ---
{resume_text[:1000]} ... (rest of resume)
--- Resume End ---

Analysis Highlights (for context, but focus on 7-second impression):
Total Score: {match_score_summary.get('total_score', 0.0):.1f}/100
Scores:
{formatted_score_summary}
Key Missing Keywords: {missing_keywords_str}
Potential Mismatches:
{mismatches_str}

Provide your response in JSON format with the following structure, strictly limiting positives and red_flags to 3 items each:
{{
  "positives": ["<list of strings, max 3 key positive points, e.g., 'Recent relevant title', 'Key skill X listed'>"],
  "red_flags": ["<list of strings, max 3 key red flags or concerns, e.g., 'Missing core skill Y', 'Too junior for role based on experience years'>"],
  "verdict": "<string, 'Proceed', 'Hold', or 'Reject'>",
  "verdict_reason": "<string, brief reasoning for the verdict based on the 7-second scan impression>"
}}

Example:
{{
  "positives": ["5+ years exp", "Python, SQL", "Cloud (AWS) mentioned"],
  "red_flags": ["No direct AI/ML leadership", "Lacks specific framework 'TensorFlow'", "Years of exp might be borderline for 'Senior'"],
  "verdict": "Hold",
  "verdict_reason": "Has core skills but AI leadership and specific framework experience needs deeper check."
}}
Focus on what a recruiter would realistically glean in a very short timeframe.
"""
