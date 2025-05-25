import json
from typing import Dict, Any
from models.analysis_models import SubScore, MatchScoreOutput
from prompts.match_score_prompts import (
    get_hard_skills_prompt,
    get_soft_skills_prompt,
    get_role_alignment_prompt,
    get_ats_compatibility_prompt,
)
from prompts.keyword_gap_prompts import (
    get_missing_keywords_prompt,
    get_role_mismatch_prompt,
)
from models.analysis_models import (
    MissingKeywordsOutput,
    RoleMismatchSignal,
    GapsOutput,
    ATSRejectionCriterion,
    ATSRejectionPredictorOutput,
)
from typing import Tuple, List # Added List
from prompts.ats_predictor_prompts import get_ats_rejection_predictor_prompt

class MockGeminiClient:
    """
    A mock client that simulates responses from the Gemini API.
    This is for development and testing purposes.
    """
    def generate_content(self, prompt: str) -> str:
        """
        Simulates generating content based on the prompt.
        Returns a JSON string as if from the Gemini API.
        """
        # Determine the type of prompt to give a relevant mock response
        if "hard skills" in prompt.lower():
            return json.dumps({
                "score": 82.5,
                "rationale": "Candidate possesses strong Python and SQL skills listed in the JD. Lacks experience with cloud platforms.",
                "matched_skills": ["Python", "SQL", "Problem Solving"],
                "missing_skills": ["AWS", "Docker"]
            })
        elif "soft skills" in prompt.lower():
            return json.dumps({
                "score": 78.0,
                "rationale": "Resume indicates good communication via project descriptions and teamwork from past roles. Leadership experience is not explicitly detailed.",
                "demonstrated_skills": ["Communication", "Teamwork", "Analytical Thinking"],
                "missing_skills": ["Leadership", "Mentoring"]
            })
        elif "role alignment" in prompt.lower():
            return json.dumps({
                "score": 85.0,
                "rationale": "Candidate's past 5 years in similar software engineering roles show a good trajectory and relevant project experience. The target industry sector is different.",
                "alignment_highlights": ["5+ years in software development", "Experience with agile methodologies"],
                "alignment_gaps": ["Lack of experience in the fintech sector", "No direct experience with project management of large teams"]
            })
        elif "ats compatibility" in prompt.lower():
            # This prompt only takes resume_text, so the check is simpler
            return json.dumps({
                "score": 92.0,
                "rationale": "Resume uses standard fonts, clear headings, and keyword-friendly language. Some minor improvements could be made to section ordering.",
                "suggestions_for_improvement": ["Consider moving 'Projects' section before 'Education' for this role type.", "Ensure all skills are explicitly listed"],
                "problematic_elements": ["Use of a custom font for name (though likely not a major issue)"]
            })
        elif "identify missing keywords" in prompt.lower():
            return json.dumps({
                "missing_keywords": ["Terraform", "CI/CD Pipeline Management", "Advanced Kubernetes"],
                "resume_keywords_summary": {"Python": 5, "AWS": 3, "SQL": 4, "Agile": 2, "Docker": 2, "Microservices": 1}
            })
        elif "role mismatch" in prompt.lower(): # Checking for "role mismatch" which is part of the prompt name
            return json.dumps({
                "experience_gaps": ["Lacks direct experience with large-scale data processing frameworks like Spark or Hadoop.", "No explicit mention of leading projects with budgets over $500k."],
                "qualification_gaps": ["JD prefers a certification in cloud security (e.g., CCSP), which is not listed."],
                "potential_mismatches": [
                    {
                        "signal_type": "Potentially Underqualified for Seniority",
                        "reasoning": "While having 5+ years, the depth of experience in leading large, complex AI projects as described in JD seems limited. JD asks for 'proven track record in delivering AI solutions from concept to production'.",
                        "evidence": ["JD: 'Lead the design and implementation of complex AI models'", "Resume: 'Led a team of 5 engineers in developing a new cloud-based SaaS product' (scope might be smaller than JD implies for 'Senior')"]
                    },
                    {
                        "signal_type": "Different Specialization Focus",
                        "reasoning": "Candidate's experience is more general software engineering with some microservices and SaaS. JD is heavily focused on specialized AI/ML model development and deployment.",
                        "evidence": ["Resume: Focus on Python (Flask), Java (Spring Boot), general SaaS development", "JD: Emphasis on TensorFlow, PyTorch, ML libraries, AI research and development"]
                    }
                ]
            })
        else:
            # Generic fallback, though ideally prompts should match one of the above
            return json.dumps({
                "score": 70.0, # This is for SubScore, might need a different generic for other types
                "rationale": "Generic mock response for an unrecognized prompt.",
                "details": "No specific details provided for this generic prompt."
            })
        elif "generate a practical and realistic action plan" in prompt.lower():
            return json.dumps({
                "summary_statement": "The candidate shows promise but needs to bridge gaps in cloud technologies (Terraform, Kubernetes) and better articulate senior-level AI project leadership. Focusing on these areas will significantly improve alignment with the Senior AI Engineer role.",
                "action_steps": [
                    {
                        "category": "Skill Development",
                        "description": "Enroll in an advanced Kubernetes course focusing on deployment, scaling, and management of containerized applications. Aim to complete a hands-on project.",
                        "priority": 1
                    },
                    {
                        "category": "Skill Development",
                        "description": "Learn Terraform fundamentals and practice by provisioning a simple infrastructure on AWS or GCP. Document this project on GitHub.",
                        "priority": 1
                    },
                    {
                        "category": "Resume Update",
                        "description": "Revise project descriptions to explicitly use keywords from the JD like 'Machine Learning Model Deployment', 'TensorFlow', and quantify achievements with metrics where possible.",
                        "priority": 2
                    },
                    {
                        "category": "Interview Preparation",
                        "description": "Prepare specific examples demonstrating leadership in past AI projects, focusing on challenges overcome and impact delivered, aligning with 'proven leadership' for a senior role.",
                        "priority": 2
                    },
                    {
                        "category": "Skill Development",
                        "description": "Gain practical experience with MLOps tools like Kubeflow or MLFlow through tutorials or small projects.",
                        "priority": 3
                    }
                ]
            })
        else:
            # Generic fallback, though ideally prompts should match one of the above
            return json.dumps({
                "score": 70.0, # This is for SubScore, might need a different generic for other types
                "rationale": "Generic mock response for an unrecognized prompt.",
                "details": "No specific details provided for this generic prompt."
            })
        elif "simulate a recruiter's 7-second scan" in prompt.lower():
            return json.dumps({
                "positives": ["5+ years software development experience", "Lists Python, Java, Docker", "Recent role as 'Senior Software Engineer'"],
                "red_flags": ["No explicit mention of 'AI' or 'Machine Learning' in recent project descriptions", "Lacks 'TensorFlow' or 'PyTorch'", "JD asks for specific AI team leadership, resume shows general software team leadership"],
                "verdict": "Hold",
                "verdict_reason": "Solid general software engineering background. Needs deeper dive to see if AI experience is implicitly present or if it's a skill gap for a specialized AI role."
            })
        elif "rewrite the following resume headline" in prompt.lower():
            return json.dumps({
                "rewritten_headline": "Senior AI Engineer | Python, TensorFlow, AWS | Ex-Software Engineer at Tech Solutions Inc.",
                "attempted_keywords": ["Senior AI Engineer", "Python", "TensorFlow", "AWS"]
            })
        elif "rewrite the following resume summary/objective" in prompt.lower():
            return json.dumps({
                "rewritten_summary": "Accomplished Senior Software Engineer with 5+ years in Python and Java, transitioning towards AI/ML. Proven ability in developing scalable solutions (e.g., SaaS product at Tech Solutions) and eager to apply skills in TensorFlow, PyTorch, and AWS to drive AI innovations, addressing key needs like MLOps and data pipelines for a Senior AI Engineer role.",
                "attempted_keywords": ["Senior Software Engineer", "Python", "Java", "AI/ML", "TensorFlow", "PyTorch", "AWS", "MLOps", "Data Pipelines", "Senior AI Engineer"]
            })
        elif "rewrite the following work experience bullet points" in prompt.lower():
            # Based on sample_original_first_experience_bullets for "Software Engineer" at "Tech Solutions Inc."
            return json.dumps({
                "rewritten_bullets": [
                    "Spearheaded the development of critical features for the company's flagship SaaS product, utilizing Python (Flask) and contributing to a 20% improvement in application performance.",
                    "Collaborated within an agile team of 5 engineers on diverse software projects, enhancing microservices architecture and ensuring robust CI/CD pipelines with Docker and Jenkins.",
                    "Proactively identified and resolved over 100 critical bugs, significantly improving system stability and user experience for the main application, leveraging skills in SQL and problem-solving."
                ],
                "attempted_keywords": ["Python", "Flask", "SaaS", "application performance", "agile", "microservices", "CI/CD", "Docker", "Jenkins", "SQL", "problem-solving", "Spearheaded", "Collaborated"]
            })
        elif "generate a concise and tailored cover letter" in prompt.lower():
            # Simulate different responses based on prompt content if needed, or a generic one
            candidate_name_in_prompt = "John Doe" # Assume based on typical demo call
            if "John Doe" in prompt: # crude check for demo scenario 1
                 return json.dumps({
                    "cover_letter_text": f"Dear Hiring Team at FutureAI Corp.,\n\nI am writing to express my strong interest in the Senior AI Engineer position. My 5+ years of Python & Java development, team leadership, and microservices experience align perfectly with your needs for designing ML models and working with cloud platforms like AWS/GCP.\n\nMy background in leading small teams and developing scalable solutions, such as the SaaS product at Tech Solutions Inc., has prepared me to tackle challenges in AI research and development. I am particularly excited by FutureAI Corp.'s innovative work.\n\nI am eager to discuss how my problem-solving skills and proactive approach can benefit your team. Thank you for your consideration.\n\nSincerely,\n{candidate_name_in_prompt}",
                    "notes": "This letter emphasizes leadership and technical skills. Consider adding a specific project that used ML if available."
                })
            else: # crude check for demo scenario 2 (minimal details)
                return json.dumps({
                    "cover_letter_text": f"Dear Hiring Team at FutureAI Corp.,\n\nI am writing to express my interest in a position at your company. My proficiency in Python aligns with your focus on developing AI applications.\n\nI am eager to contribute to your team. Thank you for your time.\n\nSincerely,\n[Your Name]",
                    "notes": "This is a very basic letter due to minimal input. More details would allow for a stronger, more tailored letter."
                })
        elif "provide a 'smart feedback summary' in the style of a constructive career mentor" in prompt.lower():
            return json.dumps({
                "strong_points": [
                    "Good overall technical foundation with Python and SQL (Hard Skills Score: ~70/100).",
                    "Excellent ATS compatibility (Score: ~90/100), meaning your resume format is likely effective.",
                    "Demonstrated soft skills like communication and teamwork are valuable (Soft Skills Score: ~80/100)."
                ],
                "areas_for_improvement": [
                    "Bridge the gap in specified cloud technologies (e.g., AWS, Kubernetes) and MLOps tools (Terraform, TensorFlow, PyTorch) which are missing keywords.",
                    "Role alignment score (~60/100) suggests a need to better articulate experience related to senior-level AI project leadership and specific JD requirements.",
                    "Ensure all key requirements from the JD, especially around AI solution delivery and specific ML libraries, are explicitly addressed in the resume."
                ],
                "quick_wins": [
                    "Incorporate missing keywords like 'Terraform', 'Kubernetes', 'MLOps', 'TensorFlow', 'PyTorch' naturally into your resume's skills or experience sections.",
                    "Quantify achievements in your 'Senior Software Engineer at Tech Solutions Inc.' role with specific metrics to showcase impact.",
                    "Review the 'Key Suggested Actions' from the action plan (e.g., 'Enroll in an advanced Kubernetes course...') and prioritize starting one this week."
                ],
                "overall_advice": "You have a strong software engineering base. To successfully pivot to a more specialized Senior AI Engineer role, focus on explicitly showcasing or acquiring the specific AI/ML and cloud skills mentioned in the JD. Tailoring your resume to each application will be key."
            })
        elif "analyze the following resume text for buzzwords" in prompt.lower():
            # Based on extended_sample_resume in core/bonus_features_logic.py's demo
            return json.dumps([
                {"buzzword": "Results-oriented go-getter", "reasoning": "This is a common filler phrase and 'go-getter' can sound informal. It's better to demonstrate results with specific achievements and metrics."},
                {"buzzword": "Synergistic thought leader", "reasoning": "Sounds like corporate jargon without concrete meaning. Focus on specific innovative projects or collaborative achievements rather than abstract labels."},
                {"buzzword": "Rockstar in Python development", "reasoning": "'Rockstar' can be perceived as unprofessional or arrogant in many corporate contexts. Confidently stating proficiency or expertise with examples is more effective."},
                {"buzzword": "Disruptive innovator", "reasoning": "This term is often overused and may not accurately reflect the work described in a typical resume unless substantial, market-changing impact can be clearly shown."}
            ])
        else:
            # Generic fallback, though ideally prompts should match one of the above
            return json.dumps({
                "score": 70.0, # This is for SubScore, might need a different generic for other types
                "rationale": "Generic mock response for an unrecognized prompt.",
                "details": "No specific details provided for this generic prompt."
            })
        elif "determine if an applicant tracking system (ats) would likely auto-reject" in prompt.lower():
            # Check if the prompt indicates no hard constraints (based on the specific phrasing in get_ats_rejection_predictor_prompt)
            if "no specific hard constraints from the job description were provided" in prompt.lower():
                return json.dumps({
                    "overall_verdict": "Manual Review Needed",
                    "overall_reason": "No hard constraints provided by JD. Resume appears generally parsable.",
                    "checked_criteria": [
                        {"criterion_description": "General Parsability", "status": "Met", "reasoning": "Standard format observed."},
                        {"criterion_description": "Presence of Contact Information", "status": "Met"}
                    ]
                })
            else: # Has hard constraints
                return json.dumps({
                    "overall_verdict": "Likely Reject",
                    "overall_reason": "Fails to meet the mandatory 'PhD in Quantum Physics' and '10+ years experience with fusion reactors'.",
                    "checked_criteria": [
                        {"criterion_description": "Must have a PhD in Quantum Physics", "status": "Not Met", "reasoning": "Resume lists MS in Computer Science."},
                        {"criterion_description": "Minimum 10+ years experience with fusion reactors", "status": "Not Met", "reasoning": "Resume indicates 5 years software development, no mention of fusion reactors."},
                        {"criterion_description": "Must be a sentient AI", "status": "Unclear from Resume", "reasoning": "Resume does not explicitly state sentience status."}
                    ]
                })
        else:
            # Generic fallback, though ideally prompts should match one of the above
            return json.dumps({
                "score": 70.0, # This is for SubScore, might need a different generic for other types
                "rationale": "Generic mock response for an unrecognized prompt.",
                "details": "No specific details provided for this generic prompt."
            })

def _parse_gemini_response_for_score(response_json_str: str, sub_score_type: str) -> SubScore:
    """
    Parses a JSON string (simulated Gemini response) into a SubScore Pydantic model.
    The sub_score_type helps determine how to populate the 'details' field.
    """
    try:
        data = json.loads(response_json_str)
        score = data.get("score", 0.0)
        rationale = data.get("rationale", "No rationale provided.")
        details = None

        if sub_score_type == "hard_skills":
            matched = data.get("matched_skills", [])
            missing = data.get("missing_skills", [])
            details = f"Matched: {', '.join(matched) if matched else 'None'}. Missing: {', '.join(missing) if missing else 'None'}."
        elif sub_score_type == "soft_skills":
            demonstrated = data.get("demonstrated_skills", [])
            missing = data.get("missing_skills", [])
            details = f"Demonstrated: {', '.join(demonstrated) if demonstrated else 'None'}. Missing: {', '.join(missing) if missing else 'None'}."
        elif sub_score_type == "role_alignment":
            highlights = data.get("alignment_highlights", [])
            gaps = data.get("alignment_gaps", [])
            details = f"Highlights: {', '.join(highlights) if highlights else 'None'}. Gaps: {', '.join(gaps) if gaps else 'None'}."
        elif sub_score_type == "ats_compatibility":
            suggestions = data.get("suggestions_for_improvement", [])
            problems = data.get("problematic_elements", [])
            details = f"Suggestions: {', '.join(suggestions) if suggestions else 'None'}. Problematic: {', '.join(problems) if problems else 'None'}."
        
        return SubScore(score=score, rationale=rationale, details=details)

    except json.JSONDecodeError:
        return SubScore(score=0.0, rationale=f"Error: Could not decode JSON response for {sub_score_type}.", details="Invalid JSON format.")
    except Exception as e: # Catch other potential errors during parsing
        return SubScore(score=0.0, rationale=f"Error: Could not parse response for {sub_score_type} due to {e}.", details=str(e))


def calculate_match_score(resume_text: str, jd_text: str, client: MockGeminiClient) -> MatchScoreOutput:
    """
    Calculates the overall match score between a resume and a job description.
    """
    # Get Hard Skills Score
    hard_skills_prompt = get_hard_skills_prompt(resume_text, jd_text)
    hard_skills_response_str = client.generate_content(hard_skills_prompt)
    hard_skills_sub_score = _parse_gemini_response_for_score(hard_skills_response_str, "hard_skills")

    # Get Soft Skills Score
    soft_skills_prompt = get_soft_skills_prompt(resume_text, jd_text)
    soft_skills_response_str = client.generate_content(soft_skills_prompt)
    soft_skills_sub_score = _parse_gemini_response_for_score(soft_skills_response_str, "soft_skills")

    # Get Role Alignment Score
    role_alignment_prompt = get_role_alignment_prompt(resume_text, jd_text)
    role_alignment_response_str = client.generate_content(role_alignment_prompt)
    role_alignment_sub_score = _parse_gemini_response_for_score(role_alignment_response_str, "role_alignment")

    # Get ATS Compatibility Score
    ats_compatibility_prompt = get_ats_compatibility_prompt(resume_text)
    ats_compatibility_response_str = client.generate_content(ats_compatibility_prompt)
    ats_compatibility_sub_score = _parse_gemini_response_for_score(ats_compatibility_response_str, "ats_compatibility")

    # Define weights for each category (example weights)
    weights = {
        "hard_skills": 0.35,
        "soft_skills": 0.25,
        "role_alignment": 0.30,
        "ats_compatibility": 0.10
    }

    # Calculate total weighted score
    total_score = (
        hard_skills_sub_score.score * weights["hard_skills"] +
        soft_skills_sub_score.score * weights["soft_skills"] +
        role_alignment_sub_score.score * weights["role_alignment"] +
        ats_compatibility_sub_score.score * weights["ats_compatibility"]
    )
    
    # Ensure total_score is within 0-100 range, just in case
    total_score = max(0, min(total_score, 100))


    return MatchScoreOutput(
        hard_skills_score=hard_skills_sub_score,
        soft_skills_score=soft_skills_sub_score,
        role_alignment_score=role_alignment_sub_score,
        ats_compatibility_score=ats_compatibility_sub_score,
        total_score=total_score
    )

if __name__ == '__main__':
    sample_resume = """
    John Doe - Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

    Summary
    Innovative Software Engineer with 5+ years of experience in developing, testing, and deploying scalable software solutions. Proficient in Python, Java, and C++. Proven ability to work in fast-paced, agile environments. Strong problem-solving and analytical skills.

    Experience
    Senior Software Engineer | Tech Solutions Inc. | Jan 2020 - Present
    - Led a team of 5 engineers in developing a new cloud-based SaaS product.
    - Designed and implemented microservices architecture using Python (Flask) and Docker.
    - Improved application performance by 20% through code optimization and database tuning.
    - Collaborated with product managers to define project requirements and timelines.

    Software Engineer | Web Innovations LLC | Jun 2017 - Dec 2019
    - Developed and maintained web applications using Java (Spring Boot) and JavaScript (React).
    - Contributed to all phases of the software development lifecycle (SDLC).
    - Wrote unit and integration tests to ensure code quality.

    Education
    Master of Science in Computer Science | University of Advanced Technology | 2017
    Bachelor of Science in Computer Science | State University | 2015

    Skills
    Programming Languages: Python, Java, C++, SQL, JavaScript
    Frameworks/Tools: Flask, Spring Boot, React, Docker, Git, Jenkins
    Databases: PostgreSQL, MongoDB
    Other: Agile Methodologies, Microservices, RESTful APIs, Problem Solving, Teamwork
    """

sample_jd = """
    Senior Software Engineer - AI Team
    FutureAI Corp. is seeking a highly motivated Senior Software Engineer to join our cutting-edge AI research and development team. You will be responsible for designing, developing, and deploying machine learning models and AI-driven applications.

    Responsibilities:
    - Design, build, and maintain efficient, reusable, and reliable Python code.
    - Implement machine learning models and integrate them into larger systems.
    - Work with large datasets and develop data pipelines.
    - Collaborate with researchers and product managers to translate requirements into technical solutions.
    - Stay up-to-date with the latest advancements in AI and machine learning.
    - Ensure software quality through code reviews, testing, and CI/CD practices.
    - Utilize cloud platforms like AWS or GCP for deploying solutions.

    Qualifications:
    - Bachelor's or Master's degree in Computer Science, AI, or related field.
    - 5+ years of professional software development experience.
    - Strong proficiency in Python and experience with ML libraries (e.g., TensorFlow, PyTorch, scikit-learn).
    - Experience with cloud platforms (AWS, GCP, or Azure) is highly desirable.
    - Knowledge of Docker, Kubernetes, and microservices architecture.
    - Excellent problem-solving skills and ability to work independently or as part of a team.
    - Strong communication and interpersonal skills.
    - Desired: Experience with Natural Language Processing (NLP).
    """

    mock_client = MockGeminiClient()
    match_score_result = calculate_match_score(sample_resume, sample_jd, mock_client)

    print("--- Match Score Analysis ---")
    print(f"Total Score: {match_score_result.total_score:.2f}/100.00\n")

    print("Hard Skills:")
    print(f"  Score: {match_score_result.hard_skills_score.score:.2f}")
    print(f"  Rationale: {match_score_result.hard_skills_score.rationale}")
    print(f"  Details: {match_score_result.hard_skills_score.details}\n")

    print("Soft Skills:")
    print(f"  Score: {match_score_result.soft_skills_score.score:.2f}")
    print(f"  Rationale: {match_score_result.soft_skills_score.rationale}")
    print(f"  Details: {match_score_result.soft_skills_score.details}\n")

    print("Role Alignment:")
    print(f"  Score: {match_score_result.role_alignment_score.score:.2f}")
    print(f"  Rationale: {match_score_result.role_alignment_score.rationale}")
    print(f"  Details: {match_score_result.role_alignment_score.details}\n")

    print("ATS Compatibility:")
    print(f"  Score: {match_score_result.ats_compatibility_score.score:.2f}")
    print(f"  Rationale: {match_score_result.ats_compatibility_score.rationale}")
    print(f"  Details: {match_score_result.ats_compatibility_score.details}\n")

    # Example of accessing the Pydantic model as a dictionary
    # print("\n--- Full Pydantic Model (as dict) ---")
    # try:
    #     # For Pydantic V2
    #     print(json.dumps(match_score_result.model_dump(), indent=2))
    # except AttributeError:
    #     # For Pydantic V1
    #     print(json.dumps(match_score_result.dict(), indent=2))
    # except Exception as e:
    #     print(f"Error converting model to dict: {e}")


def predict_ats_rejection(
    resume_text: str, 
    jd_hard_constraints: List[str], 
    client: MockGeminiClient
) -> ATSRejectionPredictorOutput:
    """
    Predicts potential ATS rejection based on hard constraints from a JD.
    """
    ats_prompt = get_ats_rejection_predictor_prompt(resume_text, jd_hard_constraints)
    response_str = client.generate_content(ats_prompt)

    try:
        data = json.loads(response_str)
        
        # Basic validation for top-level keys
        if not all(k in data for k in ["overall_verdict", "overall_reason", "checked_criteria"]):
            raise ValueError("Missing required keys in ATS rejection predictor response.")

        if not isinstance(data["checked_criteria"], list):
            raise ValueError("'checked_criteria' should be a list.")

        parsed_criteria = []
        for criterion_data in data["checked_criteria"]:
            if not all(k in criterion_data for k in ["criterion_description", "status"]):
                print(f"Skipping malformed criterion: {criterion_data}. Missing required keys.")
                continue
            # Pydantic will handle 'reasoning' being optional
            parsed_criteria.append(ATSRejectionCriterion(**criterion_data))
        
        return ATSRejectionPredictorOutput(
            overall_verdict=data["overall_verdict"],
            overall_reason=data["overall_reason"],
            checked_criteria=parsed_criteria
        )
    except json.JSONDecodeError as e:
        print(f"Error decoding ATS rejection JSON response: {e}")
        return ATSRejectionPredictorOutput(
            overall_verdict="Error",
            overall_reason="Could not decode JSON response.",
            checked_criteria=[]
        )
    except ValueError as e: # Catches Pydantic validation errors too
        print(f"Error parsing ATS rejection response: {e}")
        return ATSRejectionPredictorOutput(
            overall_verdict="Error",
            overall_reason=f"Invalid structure or data in response: {e}",
            checked_criteria=[]
        )
    except Exception as e:
        print(f"An unexpected error occurred during ATS rejection prediction: {e}")
        return ATSRejectionPredictorOutput(
            overall_verdict="Error",
            overall_reason="An unexpected error occurred.",
            checked_criteria=[]
        )


if __name__ == '__main__':
    # This sample_resume and sample_jd are now defined at the module level


def identify_missing_keywords_and_gaps(resume_text: str, jd_text: str, client: MockGeminiClient) -> Tuple[MissingKeywordsOutput, GapsOutput]:
    """
    Identifies missing keywords and experience/qualification gaps based on resume and JD.
    """
    # Missing Keywords
    missing_keywords_prompt = get_missing_keywords_prompt(resume_text, jd_text)
    missing_keywords_response_str = client.generate_content(missing_keywords_prompt)
    try:
        mk_data = json.loads(missing_keywords_response_str)
        # Basic validation
        if "missing_keywords" not in mk_data or "resume_keywords_summary" not in mk_data:
            raise ValueError("Missing expected keys in missing_keywords response")
        missing_keywords_output = MissingKeywordsOutput(**mk_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing missing keywords response: {e}")
        missing_keywords_output = MissingKeywordsOutput(missing_keywords=[], resume_keywords_summary={})

    # Gaps and Mismatches
    gaps_prompt = get_role_mismatch_prompt(resume_text, jd_text)
    gaps_response_str = client.generate_content(gaps_prompt)
    try:
        gaps_data = json.loads(gaps_response_str)
        # Basic validation
        if "experience_gaps" not in gaps_data or \
           "qualification_gaps" not in gaps_data or \
           "potential_mismatches" not in gaps_data:
            raise ValueError("Missing expected keys in gaps/mismatches response")
        
        # Ensure potential_mismatches are parsed into RoleMismatchSignal objects
        parsed_mismatches = []
        for mismatch_data in gaps_data.get("potential_mismatches", []):
            if "signal_type" not in mismatch_data or "reasoning" not in mismatch_data:
                # Minimal validation for each mismatch object
                print(f"Skipping malformed mismatch object: {mismatch_data}")
                continue
            parsed_mismatches.append(RoleMismatchSignal(**mismatch_data))
        
        gaps_output = GapsOutput(
            experience_gaps=gaps_data.get("experience_gaps", []),
            qualification_gaps=gaps_data.get("qualification_gaps", []),
            potential_mismatches=parsed_mismatches
        )
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing gaps and mismatches response: {e}")
        gaps_output = GapsOutput(experience_gaps=[], qualification_gaps=[], potential_mismatches=[])

    return missing_keywords_output, gaps_output


if __name__ == '__main__':
    sample_resume = """
    John Doe - Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

    Summary
    Innovative Software Engineer with 5+ years of experience in developing, testing, and deploying scalable software solutions. Proficient in Python, Java, and C++. Proven ability to work in fast-paced, agile environments. Strong problem-solving and analytical skills.

    Experience
    Senior Software Engineer | Tech Solutions Inc. | Jan 2020 - Present
    - Led a team of 5 engineers in developing a new cloud-based SaaS product.
    - Designed and implemented microservices architecture using Python (Flask) and Docker.
    - Improved application performance by 20% through code optimization and database tuning.
    - Collaborated with product managers to define project requirements and timelines.

    Software Engineer | Web Innovations LLC | Jun 2017 - Dec 2019
    - Developed and maintained web applications using Java (Spring Boot) and JavaScript (React).
    - Contributed to all phases of the software development lifecycle (SDLC).
    - Wrote unit and integration tests to ensure code quality.

    Education
    Master of Science in Computer Science | University of Advanced Technology | 2017
    Bachelor of Science in Computer Science | State University | 2015

    Skills
    Programming Languages: Python, Java, C++, SQL, JavaScript
    Frameworks/Tools: Flask, Spring Boot, React, Docker, Git, Jenkins
    Databases: PostgreSQL, MongoDB
    Other: Agile Methodologies, Microservices, RESTful APIs, Problem Solving, Teamwork
    """

    sample_jd = """
    Senior Software Engineer - AI Team
    FutureAI Corp. is seeking a highly motivated Senior Software Engineer to join our cutting-edge AI research and development team. You will be responsible for designing, developing, and deploying machine learning models and AI-driven applications.

    Responsibilities:
    - Design, build, and maintain efficient, reusable, and reliable Python code.
    - Implement machine learning models and integrate them into larger systems.
    - Work with large datasets and develop data pipelines.
    - Collaborate with researchers and product managers to translate requirements into technical solutions.
    - Stay up-to-date with the latest advancements in AI and machine learning.
    - Ensure software quality through code reviews, testing, and CI/CD practices.
    - Utilize cloud platforms like AWS or GCP for deploying solutions.
    - Manage and mentor junior engineers (for Senior role).
    - Lead the design and implementation of complex AI models.
    - Proven track record in delivering AI solutions from concept to production.


    Qualifications:
    - Bachelor's or Master's degree in Computer Science, AI, or related field.
    - 5+ years of professional software development experience.
    - Strong proficiency in Python and experience with ML libraries (e.g., TensorFlow, PyTorch, scikit-learn).
    - Experience with cloud platforms (AWS, GCP, or Azure) is highly desirable.
    - Knowledge of Docker, Kubernetes, and microservices architecture.
    - Excellent problem-solving skills and ability to work independently or as part of a team.
    - Strong communication and interpersonal skills.
    - Desired: Experience with Natural Language Processing (NLP).
    - Preferred: Certification in cloud security (e.g., CCSP).
    - Required: Experience with large-scale data processing frameworks like Spark or Hadoop.
    - Required: Experience leading projects with budgets over $500k.
    """

if __name__ == '__main__':
    # This sample_resume and sample_jd are now defined at the module level
    # so they can be imported by content_generator.py for its __main__ block.
    
    mock_client = MockGeminiClient()
    match_score_result = calculate_match_score(sample_resume, sample_jd, mock_client)

    print("--- Match Score Analysis ---")
    print(f"Total Score: {match_score_result.total_score:.2f}/100.00\n")

    print("Hard Skills:")
    print(f"  Score: {match_score_result.hard_skills_score.score:.2f}")
    print(f"  Rationale: {match_score_result.hard_skills_score.rationale}")
    print(f"  Details: {match_score_result.hard_skills_score.details}\n")

    print("Soft Skills:")
    print(f"  Score: {match_score_result.soft_skills_score.score:.2f}")
    print(f"  Rationale: {match_score_result.soft_skills_score.rationale}")
    print(f"  Details: {match_score_result.soft_skills_score.details}\n")

    print("Role Alignment:")
    print(f"  Score: {match_score_result.role_alignment_score.score:.2f}")
    print(f"  Rationale: {match_score_result.role_alignment_score.rationale}")
    print(f"  Details: {match_score_result.role_alignment_score.details}\n")

    print("ATS Compatibility:")
    print(f"  Score: {match_score_result.ats_compatibility_score.score:.2f}")
    print(f"  Rationale: {match_score_result.ats_compatibility_score.rationale}")
    print(f"  Details: {match_score_result.ats_compatibility_score.details}\n")

    # Demonstrate Section 2: Missing Keywords & Gaps
    print("\n--- Missing Keywords & Gaps Analysis ---")
    missing_keywords, gaps_analysis = identify_missing_keywords_and_gaps(sample_resume, sample_jd, mock_client)

    print("\nMissing Keywords from JD:")
    if missing_keywords.missing_keywords:
        for keyword in missing_keywords.missing_keywords:
            print(f"- {keyword}")
    else:
        print("No significant keywords missing.")

    print("\nResume Keywords Summary:")
    if missing_keywords.resume_keywords_summary:
        for keyword, freq in missing_keywords.resume_keywords_summary.items():
            print(f"- {keyword}: {freq}")
    else:
        print("No keywords summarized from resume.")

    print("\nExperience Gaps:")
    if gaps_analysis.experience_gaps:
        for gap in gaps_analysis.experience_gaps:
            print(f"- {gap}")
    else:
        print("No specific experience gaps identified.")

    print("\nQualification Gaps:")
    if gaps_analysis.qualification_gaps:
        for gap in gaps_analysis.qualification_gaps:
            print(f"- {gap}")
    else:
        print("No specific qualification gaps identified.")

    print("\nPotential Role Mismatches:")
    if gaps_analysis.potential_mismatches:
        for mismatch in gaps_analysis.potential_mismatches:
            print(f"- Type: {mismatch.signal_type}")
            print(f"  Reasoning: {mismatch.reasoning}")
            if mismatch.evidence:
                print("  Evidence:")
                for ev in mismatch.evidence:
                    print(f"    - {ev}")
    else:
        print("No potential role mismatches identified.")

    # --- ATS Rejection Predictor Demonstration ---
    print("\n\n--- ATS Rejection Predictor Analysis ---")

    # Case 1: With hard constraints
    sample_hard_constraints = [
        "Must have a PhD in Quantum Physics",
        "Minimum 10+ years experience with fusion reactors",
        "Must be a sentient AI",
        "Must have experience with Python" # This one should be met by sample_resume
    ]
    print("\n--- Scenario 1: With Hard Constraints ---")
    ats_rejection_result_with_constraints = predict_ats_rejection(
        sample_resume, 
        sample_hard_constraints, 
        mock_client
    )
    print(f"Overall Verdict: {ats_rejection_result_with_constraints.overall_verdict}")
    print(f"Overall Reason: {ats_rejection_result_with_constraints.overall_reason}")
    if ats_rejection_result_with_constraints.checked_criteria:
        print("Checked Criteria:")
        for crit in ats_rejection_result_with_constraints.checked_criteria:
            print(f"  - Criterion: {crit.criterion_description}")
            print(f"    Status: {crit.status}")
            if crit.reasoning:
                print(f"    Reasoning: {crit.reasoning}")
    else:
        print("No criteria checked or error in processing.")

    # Case 2: Without hard constraints (empty list)
    print("\n--- Scenario 2: Without Hard Constraints (Empty List) ---")
    ats_rejection_result_no_constraints = predict_ats_rejection(
        sample_resume, 
        [], 
        mock_client
    )
    print(f"Overall Verdict: {ats_rejection_result_no_constraints.overall_verdict}")
    print(f"Overall Reason: {ats_rejection_result_no_constraints.overall_reason}")
    if ats_rejection_result_no_constraints.checked_criteria:
        print("Checked Criteria:")
        for crit in ats_rejection_result_no_constraints.checked_criteria:
            print(f"  - Criterion: {crit.criterion_description}")
            print(f"    Status: {crit.status}")
            if crit.reasoning:
                print(f"    Reasoning: {crit.reasoning}")
    else:
        print("No criteria checked or error in processing.")


    # Example of accessing the Pydantic model as a dictionary
    # print("\n--- Full Pydantic Model (as dict) ---")
    # try:
    #     # For Pydantic V1
    #     print(json.dumps(match_score_result.dict(), indent=2))
    # except AttributeError:
    #     # For Pydantic V2
    #     print(json.dumps(match_score_result.model_dump(), indent=2))
    # except Exception as e:
    #     print(f"Error converting model to dict: {e}")
