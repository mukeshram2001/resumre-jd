from typing import List, Dict, Any, Optional

def get_smart_feedback_summary_prompt(
    match_scores: Dict[str, Any],
    missing_keywords: List[str],
    role_mismatches: List[Dict[str, Any]], # Expects list of RoleMismatchSignal-like dicts
    action_plan_summary: Optional[List[str]] # Expects list of action step descriptions
) -> str:
    """
    Generates a prompt for creating a smart feedback summary.
    Requests JSON output for strong_points, areas_for_improvement, quick_wins, and overall_advice.
    """

    # Formatting match scores
    score_details = []
    if match_scores.get("hard_skills_score"):
        score_details.append(f"- Hard Skills: {match_scores['hard_skills_score'].get('score', 'N/A'):.1f}/100 (Rationale: {match_scores['hard_skills_score'].get('rationale', 'N/A')})")
    if match_scores.get("soft_skills_score"):
        score_details.append(f"- Soft Skills: {match_scores['soft_skills_score'].get('score', 'N/A'):.1f}/100 (Rationale: {match_scores['soft_skills_score'].get('rationale', 'N/A')})")
    if match_scores.get("role_alignment_score"):
        score_details.append(f"- Role Alignment: {match_scores['role_alignment_score'].get('score', 'N/A'):.1f}/100 (Rationale: {match_scores['role_alignment_score'].get('rationale', 'N/A')})")
    if match_scores.get("ats_compatibility_score"):
        score_details.append(f"- ATS Compatibility: {match_scores['ats_compatibility_score'].get('score', 'N/A'):.1f}/100 (Rationale: {match_scores['ats_compatibility_score'].get('rationale', 'N/A')})")
    
    formatted_scores = "\n".join(score_details) if score_details else "No detailed scores provided."
    total_score_str = f"Overall Match Score: {match_scores.get('total_score', 'N/A'):.1f}/100" if match_scores.get('total_score') is not None else "Overall Match Score: N/A"


    # Formatting missing keywords
    missing_keywords_str = ", ".join(missing_keywords) if missing_keywords else "None identified."

    # Formatting role mismatches
    mismatch_details = []
    if role_mismatches:
        for mismatch in role_mismatches[:3]: # Show first 3 for brevity
            mismatch_details.append(f"- Type: {mismatch.get('signal_type', 'N/A')}, Reasoning: {mismatch.get('reasoning', 'N/A')[:150]}...") # Truncate reasoning
    formatted_mismatches = "\n".join(mismatch_details) if mismatch_details else "No significant role mismatches identified."

    # Formatting action plan summary
    action_plan_str = ""
    if action_plan_summary:
        action_plan_str = "Key Suggested Actions:\n" + "\n".join([f"- {action[:100]}..." for action in action_plan_summary[:3]]) # Show first 3 actions, truncated
    else:
        action_plan_str = "No specific action plan steps provided for summary."

    return f"""
Please provide a 'smart feedback summary' in the style of a constructive career mentor, based on the following candidate analysis.
The feedback should be encouraging yet direct, helping the candidate understand their strengths and areas for growth in relation to a target job.

Candidate Analysis Data:
{total_score_str}
Detailed Scores:
{formatted_scores}

Missing Keywords from Resume (compared to JD):
{missing_keywords_str}

Identified Role Mismatches/Gaps:
{formatted_mismatches}

{action_plan_str}

Provide your response in JSON format with the following structure:
{{
  "strong_points": ["<list of strings, key strengths identified from the analysis, be specific e.g., 'Excellent Python skills as per hard skill score'>"],
  "areas_for_improvement": ["<list of strings, key areas where the candidate can improve, be specific e.g., 'Address missing cloud technology keywords like AWS and Kubernetes'>"],
  "quick_wins": ["<list of strings, exactly 3 actionable quick wins the candidate can implement, e.g., 'Add a 'Cloud Skills' section to resume.'>"],
  "overall_advice": "<optional string, overall summary advice or encouragement, e.g., 'You have a solid foundation...'>"
}}

Focus on deriving insights from the provided data. For "quick_wins", ensure they are concrete and immediately actionable.
If data for a section (e.g., role_mismatches) is sparse or says "None identified", reflect that appropriately in your feedback rather than inventing issues.

Example for quick_wins:
["Quantify achievements in past roles with specific metrics.", "Tailor resume summary to include keywords 'AI' and 'Machine Learning'.", "Research [Company Name]'s recent projects to discuss in cover letter."]
"""
