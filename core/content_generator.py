import json
from typing import Dict, List, Any

from models.analysis_models import ActionStep, ActionPlanOutput
from prompts.action_plan_prompts import get_action_plan_prompt
from typing import Optional # Added Optional

from models.analysis_models import RecruiterLensOutput, RewrittenSection, ResumeRewriteOutput
from prompts.recruiter_lens_prompts import get_recruiter_lens_prompt
from prompts.rewrite_prompts import (
    get_rewrite_headline_prompt,
    get_rewrite_summary_prompt,
    get_rewrite_experience_bullets_prompt
)
# Assuming MockGeminiClient will be accessible from matching_logic for now
# If it's moved to a shared client module, this import would change.
from core.matching_logic import MockGeminiClient, sample_resume, sample_jd # Import sample_resume and sample_jd
from models.analysis_models import CoverLetterOutput # Added CoverLetterOutput
from prompts.cover_letter_prompts import get_cover_letter_prompt # Added get_cover_letter_prompt
from models.analysis_models import SmartFeedbackOutput # Added SmartFeedbackOutput
from prompts.feedback_prompts import get_smart_feedback_summary_prompt # Added get_smart_feedback_summary_prompt
# For the main block, we might need some sample data structures from matching_logic if we use its outputs
from core.matching_logic import MissingKeywordsOutput, MatchScoreOutput # Added MatchScoreOutput for demo

def generate_action_plan(
    match_score_summary: Dict[str, Any],
    missing_keywords: List[str],
    role_mismatches: List[Dict[str, Any]], # List of RoleMismatchSignal-like dicts
    jd_highlights: str,
    client: MockGeminiClient
) -> ActionPlanOutput:
    """
    Generates an action plan based on analysis results using a client (e.g., MockGeminiClient).
    """
    action_plan_prompt = get_action_plan_prompt(
        match_score_summary=match_score_summary,
        missing_keywords=missing_keywords,
        role_mismatches=role_mismatches,
        jd_highlights=jd_highlights
    )

    response_str = client.generate_content(action_plan_prompt)

    try:
        plan_data = json.loads(response_str)

        # Basic validation for top-level keys
        if "summary_statement" not in plan_data or "action_steps" not in plan_data:
            raise ValueError("Missing 'summary_statement' or 'action_steps' in response.")

        parsed_action_steps = []
        if not isinstance(plan_data["action_steps"], list):
            raise ValueError("'action_steps' should be a list.")

        for step_data in plan_data["action_steps"]:
            # Basic validation for each step's keys
            if not all(k in step_data for k in ["category", "description", "priority"]):
                print(f"Skipping malformed action step: {step_data}. Missing required keys.")
                continue
            try:
                # Validate priority type and range (Pydantic model will also do this)
                if not isinstance(step_data["priority"], int):
                     raise ValueError(f"Priority must be an integer for step: {step_data['description']}")
                parsed_action_steps.append(ActionStep(**step_data))
            except Exception as e: # Catch Pydantic validation errors or other issues
                 print(f"Skipping action step due to validation error: {step_data}. Error: {e}")


        return ActionPlanOutput(
            summary_statement=plan_data["summary_statement"],
            action_steps=parsed_action_steps
        )
    except json.JSONDecodeError as e:
        print(f"Error decoding action plan JSON response: {e}")
        return ActionPlanOutput(
            summary_statement="Error: Could not decode JSON response for action plan.",
            action_steps=[]
        )
    except ValueError as e:
        print(f"Error parsing action plan response: {e}")
        return ActionPlanOutput(
            summary_statement=f"Error: Invalid structure in action plan response. {e}",
            action_steps=[]
        )
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred while generating the action plan: {e}")
        return ActionPlanOutput(
            summary_statement="Error: An unexpected error occurred.",
            action_steps=[]
        )

if __name__ == '__main__':
    # 1. Sample Data
    sample_match_score_summary = {
        "total_score": 65.7, # Calculated from sub-scores
        "hard_skills_score": {"score": 70.0, "rationale": "Good Python, SQL. Missing cloud tech.", "details": "Matched: Python, SQL. Missing: AWS, Kubernetes."},
        "soft_skills_score": {"score": 80.0, "rationale": "Strong communication, teamwork.", "details": "Demonstrated: Communication, Teamwork. Missing: None apparent."},
        "role_alignment_score": {"score": 60.0, "rationale": "Some experience mismatch with senior level.", "details": "Highlights: 5yrs dev exp. Gaps: Senior level AI leadership."},
        "ats_compatibility_score": {"score": 90.0, "rationale": "Well-formatted resume.", "details": "Suggestions: None. Problematic: None."}
    }
    sample_missing_keywords = ["Terraform", "Kubernetes", "Machine Learning Model Deployment"]
    sample_role_mismatches = [
        {
            "signal_type": "Underqualified for Seniority",
            "reasoning": "Candidate has 5 years experience, but the role asks for 8+ years and proven leadership of large AI projects.",
            "evidence": ["JD: '8+ years of experience'", "JD: 'led multiple AI initiatives'", "Resume: '5 years experience'", "Resume: 'Led team of 3'"]
        },
        {
            "signal_type": "Skill Gap",
            "reasoning": "Lacks direct experience with specific MLOps tools mentioned in JD.",
            "evidence": ["JD: 'Experience with Kubeflow or MLFlow'", "Resume: Skills section does not list Kubeflow or MLFlow"]
        }
    ]
    sample_jd_highlights = """
    Seeking a Senior AI Engineer with 8+ years of experience in Python, TensorFlow, and Kubernetes.
    Must have proven experience in leading AI project lifecycles and deploying scalable machine learning models.
    Expertise in MLOps tools (Kubeflow, MLFlow) and cloud platforms (AWS preferred) is crucial.
    Strong communication and leadership skills required.
    """

    # 2. Instantiate MockGeminiClient
    # This client will be updated in the next step to handle this new prompt type.
    # For now, it might return a generic response or an error if not yet updated.
    mock_client = MockGeminiClient()

    # 3. Call generate_action_plan
    print("--- Generating Action Plan (using Mock Client) ---")
    action_plan = generate_action_plan(
        match_score_summary=sample_match_score_summary,
        missing_keywords=sample_missing_keywords,
        role_mismatches=sample_role_mismatches,
        jd_highlights=sample_jd_highlights,
        client=mock_client
    )

    # 4. Print Results
    print("\n--- Action Plan Results ---")
    print(f"Summary Statement: {action_plan.summary_statement}\n")

    if action_plan.action_steps:
        print("Action Steps:")
        for i, step in enumerate(action_plan.action_steps, 1):
            print(f"  {i}. Category: {step.category}")
            print(f"     Description: {step.description}")
            print(f"     Priority: {step.priority}\n")
    else:
        print("No action steps generated (or an error occurred).")

    print("Note: The MockGeminiClient needs to be updated to provide specific responses for action plan prompts for meaningful output.")


def generate_recruiter_lens_preview(
    resume_text: str,
    jd_text: str,
    match_score_summary: Dict[str, Any],
    missing_keywords: List[str],
    role_mismatches: List[Dict[str, Any]], # List of RoleMismatchSignal-like dicts
    client: MockGeminiClient
) -> RecruiterLensOutput:
    """
    Generates a recruiter's 7-second preview based on resume, JD, and analysis summaries.
    """
    recruiter_lens_prompt = get_recruiter_lens_prompt(
        resume_text=resume_text,
        jd_text=jd_text,
        match_score_summary=match_score_summary,
        missing_keywords=missing_keywords,
        role_mismatches=role_mismatches
    )

    response_str = client.generate_content(recruiter_lens_prompt)

    try:
        lens_data = json.loads(response_str)

        # Basic validation for top-level keys
        if not all(k in lens_data for k in ["positives", "red_flags", "verdict", "verdict_reason"]):
            raise ValueError("Missing required keys in recruiter lens response.")

        if not isinstance(lens_data["positives"], list) or \
           not isinstance(lens_data["red_flags"], list) or \
           not isinstance(lens_data["verdict"], str) or \
           not isinstance(lens_data["verdict_reason"], str):
            raise ValueError("Incorrect data types for keys in recruiter lens response.")
        
        # Pydantic will validate max_items for positives and red_flags
        return RecruiterLensOutput(**lens_data)

    except json.JSONDecodeError as e:
        print(f"Error decoding recruiter lens JSON response: {e}")
        return RecruiterLensOutput(
            positives=[],
            red_flags=[],
            verdict="Error",
            verdict_reason="Could not decode JSON response."
        )
    except ValueError as e: # Catches Pydantic validation errors too
        print(f"Error parsing recruiter lens response: {e}")
        return RecruiterLensOutput(
            positives=[],
            red_flags=[],
            verdict="Error",
            verdict_reason=f"Invalid structure or data in response: {e}"
        )
    except Exception as e:
        print(f"An unexpected error occurred while generating the recruiter lens preview: {e}")
        return RecruiterLensOutput(
            positives=[],
            red_flags=[],
            verdict="Error",
            verdict_reason="An unexpected error occurred."
        )


if __name__ == '__main__':
    # 1. Sample Data (already defined for Action Plan, reused here)
    sample_match_score_summary = {
        "total_score": 65.7, 
        "hard_skills_score": {"score": 70.0, "rationale": "Good Python, SQL. Missing cloud tech.", "details": "Matched: Python, SQL. Missing: AWS, Kubernetes."},
        "soft_skills_score": {"score": 80.0, "rationale": "Strong communication, teamwork.", "details": "Demonstrated: Communication, Teamwork. Missing: None apparent."},
        "role_alignment_score": {"score": 60.0, "rationale": "Some experience mismatch with senior level.", "details": "Highlights: 5yrs dev exp. Gaps: Senior level AI leadership."},
        "ats_compatibility_score": {"score": 90.0, "rationale": "Well-formatted resume.", "details": "Suggestions: None. Problematic: None."}
    }
    sample_missing_keywords = ["Terraform", "Kubernetes", "Machine Learning Model Deployment"]
    sample_role_mismatches = [
        {
            "signal_type": "Underqualified for Seniority",
            "reasoning": "Candidate has 5 years experience, but the role asks for 8+ years and proven leadership of large AI projects.",
            "evidence": ["JD: '8+ years of experience'", "JD: 'led multiple AI initiatives'", "Resume: '5 years experience'", "Resume: 'Led team of 3'"]
        },
        {
            "signal_type": "Skill Gap",
            "reasoning": "Lacks direct experience with specific MLOps tools mentioned in JD.",
            "evidence": ["JD: 'Experience with Kubeflow or MLFlow'", "Resume: Skills section does not list Kubeflow or MLFlow"]
        }
    ]
    sample_jd_highlights = """
    Seeking a Senior AI Engineer with 8+ years of experience in Python, TensorFlow, and Kubernetes.
    Must have proven experience in leading AI project lifecycles and deploying scalable machine learning models.
    Expertise in MLOps tools (Kubeflow, MLFlow) and cloud platforms (AWS preferred) is crucial.
    Strong communication and leadership skills required.
    """

    # Instantiate MockGeminiClient
    mock_client = MockGeminiClient()

    # --- Action Plan Generation (from previous step) ---
    print("--- Generating Action Plan (using Mock Client) ---")
    action_plan = generate_action_plan(
        match_score_summary=sample_match_score_summary,
        missing_keywords=sample_missing_keywords,
        role_mismatches=sample_role_mismatches,
        jd_highlights=sample_jd_highlights,
        client=mock_client
    )
    print("\n--- Action Plan Results ---")
    print(f"Summary Statement: {action_plan.summary_statement}\n")
    if action_plan.action_steps:
        print("Action Steps:")
        for i, step in enumerate(action_plan.action_steps, 1):
            print(f"  {i}. Category: {step.category}")
            print(f"     Description: {step.description}")
            print(f"     Priority: {step.priority}\n")
    else:
        print("No action steps generated (or an error occurred).")


    # --- Recruiter Lens Preview Generation ---
    print("\n--- Generating Recruiter Lens Preview (using Mock Client) ---")
    # Ensure sample_resume and sample_jd are available (imported from core.matching_logic)
    recruiter_preview = generate_recruiter_lens_preview(
        resume_text=sample_resume, # Defined in core.matching_logic and imported
        jd_text=sample_jd,         # Defined in core.matching_logic and imported
        match_score_summary=sample_match_score_summary,
        missing_keywords=sample_missing_keywords,
        role_mismatches=sample_role_mismatches,
        client=mock_client
    )

    print("\n--- Recruiter Lens Preview Results ---")
    print("Positives:")
    if recruiter_preview.positives:
        for p in recruiter_preview.positives:
            print(f"- {p}")
    else:
        print("None identified.")

    print("\nRed Flags:")
    if recruiter_preview.red_flags:
        for rf in recruiter_preview.red_flags:
            print(f"- {rf}")
    else:
        print("None identified.")

    print(f"\nVerdict: {recruiter_preview.verdict}")
    print(f"Reason: {recruiter_preview.verdict_reason}")

    print("\nNote: The MockGeminiClient needs to be updated to provide specific responses for recruiter lens prompts for meaningful output.")


# --- Section 6: Resume Section Auto-Rewriter ---

def _parse_rewrite_response(response_str: str, expected_content_key: str) -> Optional[RewrittenSection]:
    """
    Helper to parse JSON response for rewrite prompts.
    Returns a RewrittenSection or None if parsing fails or structure is wrong.
    'expected_content_key' should be 'rewritten_headline', 'rewritten_summary', or 'rewritten_bullets'.
    """
    try:
        data = json.loads(response_str)
        if not isinstance(data, dict) or \
           expected_content_key not in data or \
           "attempted_keywords" not in data or \
           not isinstance(data["attempted_keywords"], list):
            print(f"Error: Rewrite response JSON structure incorrect. Missing '{expected_content_key}' or 'attempted_keywords', or 'attempted_keywords' is not a list. Response: {response_str[:200]}")
            return None
        
        # The 'original_content' will be filled by the calling function, as it's not in the LLM response.
        return RewrittenSection(
            original_content="PLACEHOLDER_ORIGINAL_CONTENT", # Placeholder
            rewritten_content=data[expected_content_key],
            attempted_keywords=data["attempted_keywords"]
        )
    except json.JSONDecodeError as e:
        print(f"Error decoding rewrite JSON response: {e}. Response: {response_str[:200]}")
        return None
    except Exception as e: # Catch other potential errors like Pydantic validation
        print(f"Error creating RewrittenSection: {e}. Response: {response_str[:200]}")
        return None

def rewrite_resume_sections(
    original_headline: str,
    original_summary: str,
    original_experience_bullets: List[str], # For one specific job experience
    experience_company: str, # Company for the bullets
    experience_role: str,    # Role for the bullets
    jd_keywords: List[str],
    missing_keywords_from_resume: List[str],
    key_jd_requirements: List[str],
    target_role_title: Optional[str],
    client: MockGeminiClient
) -> ResumeRewriteOutput:
    """
    Rewrites specified resume sections (headline, summary, one experience block)
    using LLM prompts tailored for each section.
    """
    overall_summary_parts = []
    final_rewritten_headline: Optional[RewrittenSection] = None
    final_rewritten_summary: Optional[RewrittenSection] = None
    final_rewritten_experience: Optional[RewrittenSection] = None

    # 1. Rewrite Headline
    if original_headline:
        headline_prompt = get_rewrite_headline_prompt(original_headline, jd_keywords, target_role_title)
        headline_response_str = client.generate_content(headline_prompt)
        parsed_headline = _parse_rewrite_response(headline_response_str, "rewritten_headline")
        if parsed_headline:
            parsed_headline.original_content = original_headline # Set original content
            final_rewritten_headline = parsed_headline
            overall_summary_parts.append("Headline was rewritten.")
        else:
            overall_summary_parts.append("Headline rewrite failed or skipped.")

    # 2. Rewrite Summary
    if original_summary:
        summary_prompt = get_rewrite_summary_prompt(original_summary, jd_keywords, missing_keywords_from_resume, key_jd_requirements)
        summary_response_str = client.generate_content(summary_prompt)
        parsed_summary = _parse_rewrite_response(summary_response_str, "rewritten_summary")
        if parsed_summary:
            parsed_summary.original_content = original_summary # Set original content
            final_rewritten_summary = parsed_summary
            overall_summary_parts.append("Summary was rewritten.")
        else:
            overall_summary_parts.append("Summary rewrite failed or skipped.")

    # 3. Rewrite Experience Bullets (for the first provided experience)
    if original_experience_bullets and experience_company and experience_role:
        bullets_prompt = get_rewrite_experience_bullets_prompt(
            original_bullets_list=original_experience_bullets,
            company_name=experience_company,
            role_title=experience_role,
            jd_keywords=jd_keywords,
            missing_keywords_from_resume=missing_keywords_from_resume
        )
        bullets_response_str = client.generate_content(bullets_prompt)
        parsed_bullets = _parse_rewrite_response(bullets_response_str, "rewritten_bullets")
        if parsed_bullets:
            # Ensure rewritten_content is a list if original was a list
            if not isinstance(parsed_bullets.rewritten_content, list):
                 print(f"Warning: Rewritten bullets expected as list, got {type(parsed_bullets.rewritten_content)}. Attempting to use as is or skip.")
                 if isinstance(parsed_bullets.rewritten_content, str): # common error if LLM forgets list format
                     parsed_bullets.rewritten_content = [parsed_bullets.rewritten_content] # wrap it
                 else: # skip if not easily convertible
                     overall_summary_parts.append("Experience bullets rewrite failed (type error).")
                     parsed_bullets = None # reset
            
            if parsed_bullets: # check again if it was reset
                parsed_bullets.original_content = original_experience_bullets # Set original content
                final_rewritten_experience = parsed_bullets
                overall_summary_parts.append(f"Experience bullets for {experience_role} at {experience_company} were rewritten.")
        else:
            overall_summary_parts.append(f"Experience bullets rewrite for {experience_role} at {experience_company} failed or skipped.")
    
    final_overall_summary = " ".join(overall_summary_parts)
    if not final_overall_summary:
        final_overall_summary = "No sections were rewritten or all attempts failed."

    return ResumeRewriteOutput(
        overall_summary=final_overall_summary,
        rewritten_headline=final_rewritten_headline,
        rewritten_summary=final_rewritten_summary,
        rewritten_experience_bullets=final_rewritten_experience
    )


if __name__ == '__main__':
    # 1. Sample Data (already defined for Action Plan, reused here)
    sample_match_score_summary = {
        "total_score": 65.7, 
        "hard_skills_score": {"score": 70.0, "rationale": "Good Python, SQL. Missing cloud tech.", "details": "Matched: Python, SQL. Missing: AWS, Kubernetes."},
        "soft_skills_score": {"score": 80.0, "rationale": "Strong communication, teamwork.", "details": "Demonstrated: Communication, Teamwork. Missing: None apparent."},
        "role_alignment_score": {"score": 60.0, "rationale": "Some experience mismatch with senior level.", "details": "Highlights: 5yrs dev exp. Gaps: Senior level AI leadership."},
        "ats_compatibility_score": {"score": 90.0, "rationale": "Well-formatted resume.", "details": "Suggestions: None. Problematic: None."}
    }
    # Use a predefined list for missing_keywords for simplicity in this section's demo
    # In a full pipeline, this would come from the identify_missing_keywords_and_gaps function
    sample_missing_keywords_for_rewrite = ["Terraform", "Kubernetes", "MLOps", "TensorFlow", "PyTorch"]
    
    # Sample data for rewrite_resume_sections that would typically be extracted from a resume
    sample_original_headline = "Software Engineer"
    sample_original_summary = "Experienced software developer with a background in web technologies. Skilled in Python and Java. Looking for new opportunities to grow and contribute to exciting projects."
    sample_original_first_experience_bullets = [
        "Developed new features for the company's main product.",
        "Worked with a team of developers on various projects.",
        "Fixed bugs and improved application performance."
    ]
    sample_first_experience_company = "Tech Solutions Inc."
    sample_first_experience_role = "Software Engineer" # Note: resume has "Senior Software Engineer" for this role

    # Context from JD analysis (can be simplified or use more detailed from other functions)
    sample_all_jd_keywords = ["Senior AI Engineer", "Python", "Machine Learning", "TensorFlow", "PyTorch", "AWS", "GCP", "Kubernetes", "Docker", "MLOps", "Data Pipelines", "Agile"]
    sample_key_jd_requirements = [
        "5+ years of professional software development experience.",
        "Strong proficiency in Python and experience with ML libraries (e.g., TensorFlow, PyTorch, scikit-learn).",
        "Experience with cloud platforms (AWS, GCP, or Azure) is highly desirable.",
        "Knowledge of Docker, Kubernetes, and microservices architecture.",
        "Proven track record in delivering AI solutions from concept to production."
    ]
    sample_target_role_title = "Senior AI Engineer"


    # Instantiate MockGeminiClient
    mock_client = MockGeminiClient()

    # --- Action Plan Generation (from previous step, shown for context) ---
    # ... (code from previous main block for Action Plan) ...

    # --- Recruiter Lens Preview Generation (from previous step, shown for context) ---
    # ... (code from previous main block for Recruiter Lens) ...

    # --- Resume Section Auto-Rewriter Demonstration ---
    print("\n\n--- Resume Section Auto-Rewriter Analysis ---")
    
    # In a real scenario, missing_keywords_from_resume would come from identify_missing_keywords_and_gaps
    # For this demo, we'll use the sample_missing_keywords_for_rewrite defined above.
    # missing_keywords_output_from_section2, _ = identify_missing_keywords_and_gaps(sample_resume, sample_jd, mock_client)
    # actual_missing_keywords = missing_keywords_output_from_section2.missing_keywords
    
    rewrite_results = rewrite_resume_sections(
        original_headline=sample_original_headline,
        original_summary=sample_original_summary,
        original_experience_bullets=sample_original_first_experience_bullets,
        experience_company=sample_first_experience_company,
        experience_role=sample_first_experience_role, # Using the simpler role title for the bullets rewrite context
        jd_keywords=sample_all_jd_keywords,
        missing_keywords_from_resume=sample_missing_keywords_for_rewrite, # Using our sample list
        key_jd_requirements=sample_key_jd_requirements,
        target_role_title=sample_target_role_title,
        client=mock_client
    )

    print(f"Overall Rewrite Summary: {rewrite_results.overall_summary}\n")

    if rewrite_results.rewritten_headline:
        print("--- Rewritten Headline ---")
        print(f"Original: {rewrite_results.rewritten_headline.original_content}")
        print(f"Rewritten: {rewrite_results.rewritten_headline.rewritten_content}")
        print(f"Attempted Keywords: {', '.join(rewrite_results.rewritten_headline.attempted_keywords)}\n")

    if rewrite_results.rewritten_summary:
        print("--- Rewritten Summary ---")
        print(f"Original: {rewrite_results.rewritten_summary.original_content}")
        print(f"Rewritten: {rewrite_results.rewritten_summary.rewritten_content}")
        print(f"Attempted Keywords: {', '.join(rewrite_results.rewritten_summary.attempted_keywords)}\n")

    if rewrite_results.rewritten_experience_bullets:
        print(f"--- Rewritten Experience Bullets for {sample_first_experience_role} at {sample_first_experience_company} ---")
        print("Original Bullets:")
        for bullet in rewrite_results.rewritten_experience_bullets.original_content:
            print(f"- {bullet}")
        print("\nRewritten Bullets:")
        if isinstance(rewrite_results.rewritten_experience_bullets.rewritten_content, list):
            for bullet in rewrite_results.rewritten_experience_bullets.rewritten_content:
                print(f"- {bullet}")
        else: # Should not happen if parsing and LLM output are correct
            print(f"  (Unexpected format: {rewrite_results.rewritten_experience_bullets.rewritten_content})")
        print(f"Attempted Keywords: {', '.join(rewrite_results.rewritten_experience_bullets.attempted_keywords)}\n")

    print("\nNote: The MockGeminiClient needs to be updated to provide specific responses for rewrite prompts for meaningful output.")


# --- Section 7: Cover Letter Generator ---

def generate_cover_letter(
    candidate_name: Optional[str],
    top_strengths: List[str],
    jd_focus_areas: List[str],
    company_name: Optional[str],
    role_title: Optional[str],
    client: MockGeminiClient
) -> CoverLetterOutput:
    """
    Generates a cover letter using LLM.
    """
    if not top_strengths or not jd_focus_areas:
        return CoverLetterOutput(
            cover_letter_text="Error: Cannot generate cover letter without top_strengths and jd_focus_areas.",
            notes="Essential input missing (top_strengths or jd_focus_areas)."
        )

    prompt = get_cover_letter_prompt(
        candidate_name=candidate_name,
        top_strengths=top_strengths,
        jd_focus_areas=jd_focus_areas,
        company_name=company_name,
        role_title=role_title
    )
    response_str = client.generate_content(prompt)

    try:
        data = json.loads(response_str)
        if "cover_letter_text" not in data:
            raise ValueError("Missing 'cover_letter_text' in response.")
        
        # 'notes' is optional in the Pydantic model, so data.get('notes') is fine
        return CoverLetterOutput(
            cover_letter_text=data["cover_letter_text"],
            notes=data.get("notes") 
        )
    except json.JSONDecodeError as e:
        print(f"Error decoding cover letter JSON response: {e}. Response: {response_str[:200]}")
        return CoverLetterOutput(
            cover_letter_text="Error: Could not decode JSON response for cover letter.",
            notes=f"JSONDecodeError: {e}"
        )
    except ValueError as e: # Catches Pydantic validation errors too if any, or our manual ValueError
        print(f"Error parsing cover letter response: {e}. Response: {response_str[:200]}")
        return CoverLetterOutput(
            cover_letter_text="Error: Invalid structure in cover letter response.",
            notes=f"ValueError: {e}"
        )
    except Exception as e:
        print(f"An unexpected error occurred during cover letter generation: {e}")
        return CoverLetterOutput(
            cover_letter_text="Error: An unexpected error occurred.",
            notes=f"Unexpected error: {e}"
        )


if __name__ == '__main__':
    # 1. Sample Data (already defined for Action Plan, reused here)
    sample_match_score_summary = {
        "total_score": 65.7, 
        "hard_skills_score": {"score": 70.0, "rationale": "Good Python, SQL. Missing cloud tech.", "details": "Matched: Python, SQL. Missing: AWS, Kubernetes."},
        "soft_skills_score": {"score": 80.0, "rationale": "Strong communication, teamwork.", "details": "Demonstrated: Communication, Teamwork. Missing: None apparent."},
        "role_alignment_score": {"score": 60.0, "rationale": "Some experience mismatch with senior level.", "details": "Highlights: 5yrs dev exp. Gaps: Senior level AI leadership."},
        "ats_compatibility_score": {"score": 90.0, "rationale": "Well-formatted resume.", "details": "Suggestions: None. Problematic: None."}
    }
    # Use a predefined list for missing_keywords for simplicity in this section's demo
    # In a full pipeline, this would come from the identify_missing_keywords_and_gaps function
    sample_missing_keywords_for_rewrite = ["Terraform", "Kubernetes", "MLOps", "TensorFlow", "PyTorch"]
    
    # Sample data for rewrite_resume_sections that would typically be extracted from a resume
    sample_original_headline = "Software Engineer"
    sample_original_summary = "Experienced software developer with a background in web technologies. Skilled in Python and Java. Looking for new opportunities to grow and contribute to exciting projects."
    sample_original_first_experience_bullets = [
        "Developed new features for the company's main product.",
        "Worked with a team of developers on various projects.",
        "Fixed bugs and improved application performance."
    ]
    sample_first_experience_company = "Tech Solutions Inc."
    sample_first_experience_role = "Software Engineer" # Note: resume has "Senior Software Engineer" for this role

    # Context from JD analysis (can be simplified or use more detailed from other functions)
    sample_all_jd_keywords = ["Senior AI Engineer", "Python", "Machine Learning", "TensorFlow", "PyTorch", "AWS", "GCP", "Kubernetes", "Docker", "MLOps", "Data Pipelines", "Agile"]
    sample_key_jd_requirements = [
        "5+ years of professional software development experience.",
        "Strong proficiency in Python and experience with ML libraries (e.g., TensorFlow, PyTorch, scikit-learn).",
        "Experience with cloud platforms (AWS, GCP, or Azure) is highly desirable.",
        "Knowledge of Docker, Kubernetes, and microservices architecture.",
        "Proven track record in delivering AI solutions from concept to production."
    ]
    sample_target_role_title = "Senior AI Engineer"


    # Instantiate MockGeminiClient
    mock_client = MockGeminiClient()

    # --- Action Plan Generation (from previous step, shown for context) ---
    # ... (code from previous main block for Action Plan) ...

    # --- Recruiter Lens Preview Generation (from previous step, shown for context) ---
    # ... (code from previous main block for Recruiter Lens) ...
    
    # --- Resume Section Auto-Rewriter Demonstration (Shown for context) ---
    # ... (code from previous main block for Resume Rewrite) ...


    # --- Cover Letter Generator Demonstration ---
    print("\n\n--- Cover Letter Generator ---")

    # Scenario 1: With full details
    print("\n--- Scenario 1: Full Details ---")
    cover_letter_full_details = generate_cover_letter(
        candidate_name="John Doe",
        top_strengths=["5+ years of Python & Java development", "Proven ability in leading small teams (5 engineers)", "Experience with microservices architecture and Docker", "Strong problem-solving and analytical skills"],
        jd_focus_areas=["Designing and deploying machine learning models", "Working with large datasets and data pipelines", "Utilizing cloud platforms like AWS or GCP", "AI research and development"],
        company_name="FutureAI Corp.",
        role_title="Senior AI Engineer",
        client=mock_client
    )
    print("Generated Cover Letter Text:")
    print(cover_letter_full_details.cover_letter_text)
    if cover_letter_full_details.notes:
        print(f"\nNotes from LLM: {cover_letter_full_details.notes}")

    # Scenario 2: With minimal details
    print("\n\n--- Scenario 2: Minimal Details ---")
    cover_letter_minimal_details = generate_cover_letter(
        candidate_name=None, # No candidate name
        top_strengths=["Proficient in Python"], # Only one strength
        jd_focus_areas=["Develop AI applications"], # Only one focus area
        company_name="FutureAI Corp.", # Company name still provided
        role_title=None, # No specific role title
        client=mock_client
    )
    print("Generated Cover Letter Text (Minimal Details):")
    print(cover_letter_minimal_details.cover_letter_text)
    if cover_letter_minimal_details.notes:
        print(f"\nNotes from LLM: {cover_letter_minimal_details.notes}")

    # Scenario 3: Missing essential inputs
    print("\n\n--- Scenario 3: Missing Essential Inputs ---")
    cover_letter_missing_inputs = generate_cover_letter(
        candidate_name="Jane Doe",
        top_strengths=[], # Empty strengths
        jd_focus_areas=["Develop AI applications"],
        company_name="FutureAI Corp.",
        role_title="AI Developer",
        client=mock_client
    )
    print("Generated Cover Letter Text (Missing Inputs):")
    print(cover_letter_missing_inputs.cover_letter_text)
    if cover_letter_missing_inputs.notes:
        print(f"\nNotes from LLM: {cover_letter_missing_inputs.notes}")


    print("\nNote: The MockGeminiClient needs to be updated to provide specific responses for cover letter prompts for meaningful output.")


# --- Section 8: Smart Feedback Summary ---

def generate_smart_feedback(
    match_scores_data: Dict[str, Any], # Expects match_score_result.model_dump()
    missing_keywords_data: List[str], # Expects missing_keywords.missing_keywords
    gaps_data_role_mismatches: List[Dict[str, Any]], # Expects list of RoleMismatchSignal-like dicts
    action_plan_steps_summary: Optional[List[str]], # Expects list of action step descriptions
    client: MockGeminiClient
) -> SmartFeedbackOutput:
    """
    Generates a smart feedback summary based on comprehensive analysis data.
    """
    prompt = get_smart_feedback_summary_prompt(
        match_scores=match_scores_data,
        missing_keywords=missing_keywords_data,
        role_mismatches=gaps_data_role_mismatches,
        action_plan_summary=action_plan_steps_summary
    )
    response_str = client.generate_content(prompt)

    try:
        data = json.loads(response_str)
        
        # Basic validation for top-level keys
        if not all(k in data for k in ["strong_points", "areas_for_improvement", "quick_wins"]):
            raise ValueError("Missing required keys in smart feedback response (strong_points, areas_for_improvement, or quick_wins).")

        if not isinstance(data["strong_points"], list) or \
           not isinstance(data["areas_for_improvement"], list) or \
           not isinstance(data["quick_wins"], list):
            raise ValueError("Incorrect data types for 'strong_points', 'areas_for_improvement', or 'quick_wins' in smart feedback response; expected lists.")
        
        # Pydantic will validate max_items for quick_wins.
        # 'overall_advice' is optional.
        return SmartFeedbackOutput(**data)

    except json.JSONDecodeError as e:
        print(f"Error decoding smart feedback JSON response: {e}. Response: {response_str[:200]}")
        return SmartFeedbackOutput(
            strong_points=[],
            areas_for_improvement=[],
            quick_wins=[],
            overall_advice=f"Error: Could not decode JSON response. ({e})"
        )
    except ValueError as e: # Catches Pydantic validation errors or our manual ValueErrors
        print(f"Error parsing smart feedback response: {e}. Response: {response_str[:200]}")
        return SmartFeedbackOutput(
            strong_points=[],
            areas_for_improvement=[],
            quick_wins=[],
            overall_advice=f"Error: Invalid structure or data in response. ({e})"
        )
    except Exception as e:
        print(f"An unexpected error occurred during smart feedback generation: {e}")
        return SmartFeedbackOutput(
            strong_points=[],
            areas_for_improvement=[],
            quick_wins=[],
            overall_advice=f"Error: An unexpected error occurred. ({e})"
        )


if __name__ == '__main__':
    # 1. Sample Data (already defined for Action Plan, reused here)
    sample_match_score_summary = {
        "total_score": 65.7, 
        "hard_skills_score": {"score": 70.0, "rationale": "Good Python, SQL. Missing cloud tech.", "details": "Matched: Python, SQL. Missing: AWS, Kubernetes."},
        "soft_skills_score": {"score": 80.0, "rationale": "Strong communication, teamwork.", "details": "Demonstrated: Communication, Teamwork. Missing: None apparent."},
        "role_alignment_score": {"score": 60.0, "rationale": "Some experience mismatch with senior level.", "details": "Highlights: 5yrs dev exp. Gaps: Senior level AI leadership."},
        "ats_compatibility_score": {"score": 90.0, "rationale": "Well-formatted resume.", "details": "Suggestions: None. Problematic: None."}
    }
    # Use a predefined list for missing_keywords for simplicity in this section's demo
    # In a full pipeline, this would come from the identify_missing_keywords_and_gaps function
    sample_missing_keywords_for_rewrite = ["Terraform", "Kubernetes", "MLOps", "TensorFlow", "PyTorch"]
    
    # Sample data for rewrite_resume_sections that would typically be extracted from a resume
    sample_original_headline = "Software Engineer"
    sample_original_summary = "Experienced software developer with a background in web technologies. Skilled in Python and Java. Looking for new opportunities to grow and contribute to exciting projects."
    sample_original_first_experience_bullets = [
        "Developed new features for the company's main product.",
        "Worked with a team of developers on various projects.",
        "Fixed bugs and improved application performance."
    ]
    sample_first_experience_company = "Tech Solutions Inc."
    sample_first_experience_role = "Software Engineer" # Note: resume has "Senior Software Engineer" for this role

    # Context from JD analysis (can be simplified or use more detailed from other functions)
    sample_all_jd_keywords = ["Senior AI Engineer", "Python", "Machine Learning", "TensorFlow", "PyTorch", "AWS", "GCP", "Kubernetes", "Docker", "MLOps", "Data Pipelines", "Agile"]
    sample_key_jd_requirements = [
        "5+ years of professional software development experience.",
        "Strong proficiency in Python and experience with ML libraries (e.g., TensorFlow, PyTorch, scikit-learn).",
        "Experience with cloud platforms (AWS, GCP, or Azure) is highly desirable.",
        "Knowledge of Docker, Kubernetes, and microservices architecture.",
        "Proven track record in delivering AI solutions from concept to production."
    ]
    sample_target_role_title = "Senior AI Engineer"


    # Instantiate MockGeminiClient
    mock_client = MockGeminiClient()

    # --- Action Plan Generation (from previous step, shown for context) ---
    # ... (code from previous main block for Action Plan) ...
    # For Smart Feedback, we need the action_plan.action_steps
    action_plan_for_feedback = generate_action_plan(
        match_score_summary=sample_match_score_summary,
        missing_keywords=sample_missing_keywords_for_rewrite, # Using the rewrite list as an example
        role_mismatches=[ # Sample role mismatches for action plan context
            {"signal_type": "Skill Gap", "reasoning": "Lacks specific cloud tech.", "evidence": ["JD: AWS, Kubernetes"]},
            {"signal_type": "Experience Level", "reasoning": "Needs to show more senior project leadership.", "evidence": ["JD: 'Lead complex AI models'"]}
        ],
        jd_highlights="Focus on AI, Python, Cloud, and Leadership.",
        client=mock_client
    )
    sample_action_plan_steps_summary = [step.description for step in action_plan_for_feedback.action_steps] if action_plan_for_feedback.action_steps else []


    # --- Recruiter Lens Preview Generation (from previous step, shown for context) ---
    # ... (code from previous main block for Recruiter Lens) ...
    
    # --- Resume Section Auto-Rewriter Demonstration (Shown for context) ---
    # ... (code from previous main block for Resume Rewrite) ...

    # --- Cover Letter Generator Demonstration (Shown for context) ---
    # ... (code from previous main block for Cover Letter) ...


    # --- Smart Feedback Summary Demonstration ---
    print("\n\n--- Smart Feedback Summary ---")

    # Prepare inputs for smart feedback
    # 1. match_scores_data: Use sample_match_score_summary (it's already a dict)
    # 2. missing_keywords_data: Use sample_missing_keywords_for_rewrite
    # 3. gaps_data_role_mismatches: Create a sample
    sample_gaps_role_mismatches_for_feedback = [
        {"signal_type": "Skill Gap", "reasoning": "Candidate needs to demonstrate experience with specific cloud technologies like AWS and Kubernetes as per JD.", "evidence": ["JD: Requires AWS, Kubernetes", "Resume: Does not list these explicitly"]},
        {"signal_type": "Experience Depth", "reasoning": "While having 5 years, the resume needs to better articulate leadership in complex AI projects to match 'Senior AI Engineer' expectations.", "evidence": ["JD: 'Proven track record in delivering AI solutions'", "Resume: 'Led a team of 5' - good, but needs more AI focus."]}
    ]
    # 4. action_plan_steps_summary: Use from the action_plan generated above

    smart_feedback_result = generate_smart_feedback(
        match_scores_data=sample_match_score_summary, # This is already a dict
        missing_keywords_data=sample_missing_keywords_for_rewrite,
        gaps_data_role_mismatches=sample_gaps_role_mismatches_for_feedback,
        action_plan_steps_summary=sample_action_plan_steps_summary,
        client=mock_client
    )

    print("\n--- Smart Feedback Results ---")
    print("\nStrong Points:")
    if smart_feedback_result.strong_points:
        for point in smart_feedback_result.strong_points:
            print(f"- {point}")
    else:
        print("None identified or error in generation.")

    print("\nAreas for Improvement:")
    if smart_feedback_result.areas_for_improvement:
        for area in smart_feedback_result.areas_for_improvement:
            print(f"- {area}")
    else:
        print("None identified or error in generation.")

    print("\nQuick Wins (Max 3):")
    if smart_feedback_result.quick_wins:
        for win in smart_feedback_result.quick_wins:
            print(f"- {win}")
    else:
        print("None identified or error in generation.")
    
    if smart_feedback_result.overall_advice:
        print(f"\nOverall Advice: {smart_feedback_result.overall_advice}")
    else:
        print("\nNo overall advice provided or error in generation.")

    print("\nNote: The MockGeminiClient needs to be updated to provide specific responses for smart feedback prompts for meaningful output.")


# --- Section 9: Public Resume Feedback Mode ---

def prepare_public_feedback_card_data(
    resume_text: str, # Full resume text for anonymization context
    target_role: str, # From user input or inferred
    match_score_output: MatchScoreOutput,
    missing_keywords_output: MissingKeywordsOutput,
    smart_feedback_output: SmartFeedbackOutput,
    # Potentially other inputs like GapsOutput if relevant for red_flags
) -> PublicFeedbackCard:
    """
    Prepares the data for a PublicFeedbackCard by anonymizing parts of the resume
    and selecting key insights from various analysis outputs.

    NOTE: Actual LLM-based anonymization is complex and NOT implemented in this subtask.
    This function will use placeholders or simple redaction for demonstration.
    """

    # Step 1: Anonymize resume summary and target role (Conceptual)
    # This is a placeholder for a much more complex anonymization process.
    # For now, we'll use a simple approach or predefined anonymized text.
    # A real implementation might involve NER to find PII and replace it,
    # or an LLM call to summarize and anonymize.
    
    anonymized_resume_summary = f"Experienced professional with skills in key areas from the resume (e.g., Python, project management). Original summary length: {len(resume_text.splitlines())} lines."
    if len(resume_text) > 200:
        anonymized_resume_summary = resume_text[:100].replace("\n", " ") + "... (summary of skills and experience)"
    else:
        anonymized_resume_summary = "Summary of skills and experience from the resume."
        
    anonymized_target_role = f"Seeking a {target_role.lower()} role in the tech industry." # Simple anonymization

    # Step 2: Select data from other analysis outputs
    overall_match_score_val = int(match_score_output.total_score) if match_score_output.total_score is not None else 0
    
    # Use up to 5 key missing keywords
    key_missing_keywords = missing_keywords_output.missing_keywords[:5] if missing_keywords_output else []
    
    # Use positives from SmartFeedback or RecruiterLens (example: using SmartFeedback's strong_points)
    key_positives = smart_feedback_output.strong_points[:3] if smart_feedback_output else []
    
    # Use red flags from SmartFeedback's areas_for_improvement or RecruiterLens
    # For this example, let's derive from areas_for_improvement
    key_red_flags = smart_feedback_output.areas_for_improvement[:3] if smart_feedback_output else []
    
    # Use quick wins from SmartFeedback
    key_quick_wins = smart_feedback_output.quick_wins[:3] if smart_feedback_output else []

    # Step 3: Craft a request_for_feedback_prompt (can be dynamic or a few templates)
    # This example creates a generic one, but it could be more specific based on analysis.
    feedback_request_parts = ["Given my anonymized profile above and targeting a general"]
    feedback_request_parts.append(f"'{anonymized_target_role}',")
    if key_red_flags:
        feedback_request_parts.append(f"and knowing areas like '{key_red_flags[0]}' might be concerns,")
    feedback_request_parts.append("what's one key area I should focus on improving in my resume or experience to better align for such roles?")
    request_for_feedback = " ".join(feedback_request_parts)
    
    # Step 4: Assemble PublicFeedbackCard
    public_card = PublicFeedbackCard(
        anonymized_resume_summary=anonymized_resume_summary,
        anonymized_target_role=anonymized_target_role,
        overall_match_score=overall_match_score_val,
        key_missing_keywords_summary=key_missing_keywords,
        key_positives=key_positives,
        key_red_flags=key_red_flags,
        key_quick_wins=key_quick_wins,
        request_for_feedback_prompt=request_for_feedback
    )
    
    return public_card
