import json
from typing import List, Dict, Any

# Assuming MockGeminiClient will be accessible from matching_logic for now
# If it's moved to a shared client module, this import would change.
from core.matching_logic import MockGeminiClient, sample_resume, sample_jd # For demo
from models.analysis_models import TemplateSuggestion, BuzzwordAnalysis
from prompts.bonus_prompts import get_buzzword_analysis_prompt

# --- Section 10: Bonus Add-Ons ---

def suggest_ats_templates() -> List[TemplateSuggestion]:
    """
    Returns a hardcoded list of ATS-friendly resume template suggestions.
    No LLM call involved.
    """
    return [
        TemplateSuggestion(
            template_name="Harvard ATS Resume Template",
            url="https://cdn-careerservices.fas.harvard.edu/wp-content/uploads/sites/161/2023/08/Harvard-Resume-Template-ATS.pdf",
            description="A clean, widely-used ATS-friendly template from Harvard Extension School."
        ),
        TemplateSuggestion(
            template_name="ResumeWorded ATS Templates",
            url="https://www.resumeworded.com/resume-templates/",
            description="Offers a collection of ATS-optimized templates with advice."
        ),
        TemplateSuggestion(
            template_name="Jobscan ATS Resume Templates",
            url="https://www.jobscan.co/resume-templates",
            description="Provides free ATS-compatible resume templates and examples."
        )
    ]

def analyze_for_irrelevant_buzzwords(
    resume_text: str, 
    jd_text: str, 
    client: MockGeminiClient
) -> List[BuzzwordAnalysis]:
    """
    Identifies irrelevant or potentially negative buzzwords in the resume
    in the context of the job description using an LLM.
    """
    if not resume_text.strip():
        print("Warning: Resume text is empty. Skipping buzzword analysis.")
        return []

    prompt = get_buzzword_analysis_prompt(resume_text, jd_text)
    response_str = client.generate_content(prompt)
    
    try:
        data = json.loads(response_str)
        if not isinstance(data, list):
            print(f"Error: Buzzword analysis response is not a list. Response: {response_str[:200]}")
            return []

        analyzed_buzzwords = []
        for item in data:
            if not isinstance(item, dict) or "buzzword" not in item or "reasoning" not in item:
                print(f"Skipping malformed buzzword item: {item}. Missing 'buzzword' or 'reasoning'.")
                continue
            try:
                analyzed_buzzwords.append(BuzzwordAnalysis(**item))
            except Exception as e: # Catch Pydantic validation errors
                print(f"Skipping buzzword item due to validation error: {item}. Error: {e}")
        
        return analyzed_buzzwords
        
    except json.JSONDecodeError as e:
        print(f"Error decoding buzzword analysis JSON response: {e}. Response: {response_str[:200]}")
        return []
    except Exception as e: # Catch other unexpected errors
        print(f"An unexpected error occurred during buzzword analysis: {e}")
        return []

if __name__ == '__main__':
    print("--- Bonus Add-Ons Demonstration ---")

    # 1. Suggest ATS Templates
    print("\n--- ATS Template Suggestions ---")
    template_suggestions = suggest_ats_templates()
    if template_suggestions:
        for i, template in enumerate(template_suggestions, 1):
            print(f"{i}. Name: {template.template_name}")
            print(f"   URL: {template.url}")
            if template.description:
                print(f"   Description: {template.description}")
            print("-" * 20)
    else:
        print("No template suggestions available.")

    # 2. Analyze for Irrelevant Buzzwords
    print("\n\n--- Irrelevant Buzzword Analysis ---")
    # Using sample_resume and sample_jd imported from core.matching_logic for demonstration
    
    # Let's add some potential buzzwords to the sample_resume for the demo
    extended_sample_resume = sample_resume + """

    Additional Attributes:
    - Results-oriented go-getter
    - Synergistic thought leader
    - Rockstar in Python development
    - Disruptive innovator
    """
    
    mock_client_instance = MockGeminiClient()
    
    buzzwords_analysis = analyze_for_irrelevant_buzzwords(
        resume_text=extended_sample_resume, 
        jd_text=sample_jd, # sample_jd from core.matching_logic
        client=mock_client_instance
    )
    
    if buzzwords_analysis:
        print("Identified Potentially Irrelevant Buzzwords:")
        for i, analysis in enumerate(buzzwords_analysis, 1):
            print(f"{i}. Buzzword: '{analysis.buzzword}'")
            print(f"   Reasoning: {analysis.reasoning}")
            print("-" * 20)
    else:
        print("No irrelevant buzzwords identified or an error occurred.")
    
    print("\nNote: The MockGeminiClient needs to be updated to provide specific responses for buzzword analysis prompts for meaningful output.")
