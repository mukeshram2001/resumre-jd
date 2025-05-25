from typing import List, Dict, Any

def get_action_plan_prompt(
    match_score_summary: Dict[str, Any],
    missing_keywords: List[str],
    role_mismatches: List[Dict[str, Any]], # Expects list of RoleMismatchSignal like dicts
    jd_highlights: str
) -> str:
    """
    Generates a prompt for the Gemini API to create an action plan for a candidate.
    Requests JSON output.
    """

    # Convert complex objects to simpler string representations for the prompt
    formatted_score_summary = "\n".join([f"- {key.replace('_', ' ').title()}: {value['score']:.1f}/100 (Rationale: {value['rationale']})" for key, value in match_score_summary.items() if key.endswith('_score')])
    
    formatted_mismatches = []
    if role_mismatches:
        for mismatch in role_mismatches:
            evidence_str = ", ".join(mismatch.get('evidence', []))
            formatted_mismatches.append(
                f"- Type: {mismatch.get('signal_type', 'N/A')}\n"
                f"  Reasoning: {mismatch.get('reasoning', 'N/A')}\n"
                f"  Evidence: {evidence_str if evidence_str else 'N/A'}"
            )
    else:
        formatted_mismatches.append("- None identified.")
    
    mismatches_str = "\n".join(formatted_mismatches)
    missing_keywords_str = ", ".join(missing_keywords) if missing_keywords else "None"

    return f"""
Based on the following analysis of a candidate's resume against a job description, please generate a practical and realistic action plan. The plan should help the candidate improve their profile and better align with the job requirements.

Job Description Highlights:
{jd_highlights}

Candidate Analysis Summary:
Overall Match Score: {match_score_summary.get('total_score', 0.0):.1f}/100

Category Scores:
{formatted_score_summary}

Identified Missing Keywords from JD:
{missing_keywords_str}

Identified Role Mismatches/Gaps:
{mismatches_str}

Provide your response in JSON format with the following structure:
{{
  "summary_statement": "<string, a brief summary of the candidate's current standing and key areas for improvement, tailored to the analysis provided>",
  "action_steps": [
    {{
      "category": "<string, e.g., 'Skill Development', 'Resume Update', 'Networking', 'Project Work', 'Interview Preparation'>",
      "description": "<string, detailed and actionable description of the step>",
      "priority": <integer, 1-5, where 1 is highest priority>
    }}
  ]
}}

Focus on providing concrete, actionable steps. Prioritize actions that will have the most impact.
For example, if 'Terraform' is a missing keyword and 'AWS' experience is low, an action could be:
"Category: Skill Development, Description: Undertake a hands-on project using Terraform to deploy a service on AWS, focusing on core Terraform concepts and AWS integration., Priority: 1"
Another example for resume update:
"Category: Resume Update, Description: Quantify achievements in the 'Senior Software Engineer at Tech Solutions Inc.' role by adding specific metrics related to the SaaS product's performance improvement or team leadership., Priority: 2"
"""
