from pydantic import BaseModel, Field
from typing import List, Optional

class SubScore(BaseModel):
    score: float = Field(..., description="Score for the sub-category, out of 100")
    rationale: str = Field(..., description="Rationale behind the score")
    details: Optional[str] = Field(None, description="Additional details, like matched/missing skills")

class MatchScoreOutput(BaseModel):
    hard_skills_score: SubScore
    soft_skills_score: SubScore
    role_alignment_score: SubScore
    ats_compatibility_score: SubScore
    total_score: float = Field(..., description="Overall weighted score, out of 100")
    # TODO: Implement validator for total_score if needed for Pydantic V1/V2
    # @validator('total_score', pre=True, always=True)
    # def calculate_total_score(cls, v, values):
    #     # Implement weighted scoring logic if specific weights are defined
    #     # For now, a simple average or sum might suffice
    #     # This is a placeholder
    #     total = 0
    #     num_scores = 0
    #     if 'hard_skills_score' in values:
    #         total += values['hard_skills_score'].score
    #         num_scores +=1
    #     if 'soft_skills_score' in values:
    #         total += values['soft_skills_score'].score
    #         num_scores +=1
    #     # Add other scores similarly
    #     return total / num_scores if num_scores > 0 else 0

    class Config:
        # For Pydantic V2, use model_config instead of Config
        # model_config = {
        #     "json_schema_extra": {
        #         "examples": [
        #             {
        #                 "hard_skills_score": {"score": 85.0, "rationale": "Good match in programming languages."},
        #                 "soft_skills_score": {"score": 75.0, "rationale": "Demonstrates teamwork and communication."},
        #                 "role_alignment_score": {"score": 80.0, "rationale": "Experience aligns with role requirements."},
        #                 "ats_compatibility_score": {"score": 90.0, "rationale": "Resume is well-formatted for ATS."},
        #                 "total_score": 82.5
        #             }
        #         ]
        #     }
        # }
        # For Pydantic V1
        schema_extra = {
            "examples": [
                {
                    "hard_skills_score": {"score": 85.0, "rationale": "Good match in programming languages."},
                    "soft_skills_score": {"score": 75.0, "rationale": "Demonstrates teamwork and communication."},
                    "role_alignment_score": {"score": 80.0, "rationale": "Experience aligns with role requirements."},
                    "ats_compatibility_score": {"score": 90.0, "rationale": "Resume is well-formatted for ATS."},
                    "total_score": 82.5
                }
            ]
        }

class MissingKeywordsOutput(BaseModel):
    missing_keywords: List[str] = Field(..., description="Keywords from JD not found in resume")
    resume_keywords_summary: Dict[str, int] = Field(..., description="Summary of relevant keywords found in resume and their frequencies")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "missing_keywords": ["Terraform", "CI/CD Pipeline Management"],
                    "resume_keywords_summary": {"Python": 5, "AWS": 3, "SQL": 4, "Agile": 2}
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "missing_keywords": ["Terraform", "CI/CD Pipeline Management"],
        #                "resume_keywords_summary": {"Python": 5, "AWS": 3, "SQL": 4, "Agile": 2}
        #            }
        #        ]
        #    }
        # }

class ActionStep(BaseModel):
    category: str = Field(..., description="Category of the action, e.g., 'Skill Development', 'Resume Update', 'Networking'")
    description: str = Field(..., description="Detailed description of the action step")
    priority: int = Field(..., ge=1, le=5, description="Priority of the action step (1=Highest, 5=Lowest)")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "category": "Skill Development",
                    "description": "Enroll in an online course for Terraform and complete a hands-on project.",
                    "priority": 1
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "category": "Skill Development",
        #                "description": "Enroll in an online course for Terraform and complete a hands-on project.",
        #                "priority": 1
        #            }
        #        ]
        #    }
        # }

class ActionPlanOutput(BaseModel):
    summary_statement: str = Field(..., description="A brief summary of the candidate's current standing and key areas for improvement.")
    action_steps: List[ActionStep] = Field(..., description="A list of actionable steps for the candidate.")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "summary_statement": "The candidate has a good foundation but needs to address specific skill gaps in cloud technologies and better highlight project impacts to align with the Senior AI Engineer role.",
                    "action_steps": [
                        {
                            "category": "Skill Development",
                            "description": "Complete an advanced Kubernetes course focusing on deployment and scaling.",
                            "priority": 1
                        },
                        {
                            "category": "Resume Update",
                            "description": "Quantify achievements in past roles with specific metrics, especially for the SaaS product at Tech Solutions Inc.",
                            "priority": 2
                        }
                    ]
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "summary_statement": "The candidate has a good foundation but needs to address specific skill gaps in cloud technologies and better highlight project impacts to align with the Senior AI Engineer role.",
        #                "action_steps": [
        #                    {
        #                        "category": "Skill Development",
        #                        "description": "Complete an advanced Kubernetes course focusing on deployment and scaling.",
        #                        "priority": 1
        #                    },
        #                    {
        #                        "category": "Resume Update",
        #                        "description": "Quantify achievements in past roles with specific metrics, especially for the SaaS product at Tech Solutions Inc.",
        #                        "priority": 2
        #                    }
        #                ]
        #            }
        #        ]
        #    }
        # }

class RecruiterLensOutput(BaseModel):
    positives: List[str] = Field(..., max_items=3, description="Up to 3 key positive points a recruiter would notice in a quick scan.")
    red_flags: List[str] = Field(..., max_items=3, description="Up to 3 key red flags or concerns.")
    verdict: str = Field(..., description="A quick verdict: 'Proceed', 'Hold', or 'Reject'.")
    verdict_reason: str = Field(..., description="Brief reasoning for the verdict based on the 7-second scan impression.")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "positives": ["5+ years in software development", "Python & Java experience", "Led a small team"],
                    "red_flags": ["Missing direct AI/ML project leadership", "Lacks specific cloud certifications mentioned in JD", "Experience level might be slightly below 'Senior AI Engineer' ask"],
                    "verdict": "Hold",
                    "verdict_reason": "Solid software engineering background but needs closer review for depth in AI leadership and specific cloud skills against other candidates."
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "positives": ["5+ years in software development", "Python & Java experience", "Led a small team"],
        #                "red_flags": ["Missing direct AI/ML project leadership", "Lacks specific cloud certifications mentioned in JD", "Experience level might be slightly below 'Senior AI Engineer' ask"],
        #                "verdict": "Hold",
        #                "verdict_reason": "Solid software engineering background but needs closer review for depth in AI leadership and specific cloud skills against other candidates."
        #            }
        #        ]
        #    }
        # }

class ATSRejectionCriterion(BaseModel):
    criterion_description: str = Field(..., description="Description of the hard constraint checked (e.g., 'Must have a Bachelor's degree in CS')")
    status: str = Field(..., description="Status of this criterion: 'Met', 'Not Met', 'Unclear from Resume'")
    reasoning: Optional[str] = Field(None, description="Brief reasoning if status is 'Not Met' or 'Unclear'")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "criterion_description": "Must have PMP Certification",
                    "status": "Not Met",
                    "reasoning": "PMP Certification is not listed in the skills or education sections."
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "criterion_description": "Must have PMP Certification",
        #                "status": "Not Met",
        #                "reasoning": "PMP Certification is not listed in the skills or education sections."
        #            }
        #        ]
        #    }
        # }

class ATSRejectionPredictorOutput(BaseModel):
    overall_verdict: str = Field(..., description="Overall ATS verdict: 'Likely Pass', 'Likely Reject', 'Manual Review Needed'")
    overall_reason: str = Field(..., description="Brief overall reasoning for the verdict.")
    checked_criteria: List[ATSRejectionCriterion] = Field(default_factory=list, description="List of hard criteria checked and their status.")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "overall_verdict": "Likely Reject",
                    "overall_reason": "Fails to meet mandatory degree requirement.",
                    "checked_criteria": [
                        {"criterion_description": "Must have a Bachelor's degree in Computer Science", "status": "Not Met", "reasoning": "Degree listed is 'Bachelor of Arts in History'"},
                        {"criterion_description": "Must have 5+ years of Java experience", "status": "Met", "reasoning": None},
                        {"criterion_description": "Must be eligible to work in the US without sponsorship", "status": "Unclear from Resume"}
                    ]
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "overall_verdict": "Likely Reject",
        #                "overall_reason": "Fails to meet mandatory degree requirement.",
        #                "checked_criteria": [
        #                    {"criterion_description": "Must have a Bachelor's degree in Computer Science", "status": "Not Met", "reasoning": "Degree listed is 'Bachelor of Arts in History'"},
        #                    {"criterion_description": "Must have 5+ years of Java experience", "status": "Met", "reasoning": None},
        #                    {"criterion_description": "Must be eligible to work in the US without sponsorship", "status": "Unclear from Resume"}
        #                ]
        #            }
        #        ]
        #    }
        # }

class RewrittenSection(BaseModel):
    original_content: Any = Field(..., description="The original text or list of strings.")
    rewritten_content: Any = Field(..., description="The rewritten text or list of strings.")
    attempted_keywords: List[str] = Field(default_factory=list, description="Keywords the rewrite attempted to incorporate.")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "original_content": "Developed web apps.",
                    "rewritten_content": "Engineered and deployed scalable web applications using Python and Django, incorporating RESTful APIs.",
                    "attempted_keywords": ["Python", "Django", "RESTful APIs", "scalable"]
                }
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }

# --- Section 9: Public Resume Feedback Mode ---
class PublicFeedbackCard(BaseModel):
    anonymized_resume_summary: str = Field(..., description="A brief, anonymized summary of the resume's key experience or skills.")
    anonymized_target_role: str = Field(..., description="Anonymized or generalized target role (e.g., 'Senior Software Engineer in Tech').")
    overall_match_score: int = Field(..., ge=0, le=100, description="The overall match score percentage.")
    key_missing_keywords_summary: List[str] = Field(default_factory=list, max_items=5, description="Up to 5 key missing keywords that are important for the role.")
    key_positives: List[str] = Field(default_factory=list, max_items=3, description="Up to 3 key positive aspects of the resume for this role.")
    key_red_flags: List[str] = Field(default_factory=list, max_items=3, description="Up to 3 key concerns or red flags for this role.")
    key_quick_wins: List[str] = Field(default_factory=list, max_items=3, description="Up to 3 actionable quick wins for improvement.")
    request_for_feedback_prompt: str = Field(..., description="A specific question or prompt asking for community feedback (e.g., 'How can I better showcase my project leadership skills for a Senior AI role?').")
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "anonymized_resume_summary": "Experienced (5+ years) software developer with skills in Python, Java, and web development. Led a small team for a SaaS product.",
                    "anonymized_target_role": "Senior AI Engineer in a mid-sized tech company",
                    "overall_match_score": 65,
                    "key_missing_keywords_summary": ["TensorFlow", "PyTorch", "MLOps", "Cloud AI Services", "NLP"],
                    "key_positives": ["Strong Python experience", "Team leadership experience", "SaaS product development background"],
                    "key_red_flags": ["Lacks explicit AI/ML project leadership", "Missing specific ML framework keywords", "Cloud experience not detailed for AI"],
                    "key_quick_wins": ["Detail specific AI/ML contributions in past projects.", "Add a 'Cloud Skills for AI' section.", "Quantify impact of leadership roles."],
                    "request_for_feedback_prompt": "Given my background in general software engineering and recent focus on learning AI/ML, how can I best reframe my experience to be more attractive for Senior AI Engineer roles requiring proven AI project delivery?"
                }
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }

# --- Section 10: Bonus Add-Ons ---
class TemplateSuggestion(BaseModel):
    template_name: str
    url: str # Field(..., pattern="^https?://.+") # Consider adding URL validation if needed
    description: Optional[str] = None
    
    class Config:
        schema_extra = {
            "examples": [
                {"template_name": "Harvard ATS Resume Template", "url": "https://cdn-careerservices.fas.harvard.edu/wp-content/uploads/sites/161/2023/08/Harvard-Resume-Template-ATS.pdf", "description": "A clean, ATS-friendly template from Harvard Extension School."}
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }

class BuzzwordAnalysis(BaseModel):
    buzzword: str = Field(..., description="The identified buzzword or jargon.")
    reasoning: str = Field(..., description="Explanation why this buzzword might be considered irrelevant, overused, or potentially negative in the context of the target JD.")
    
    class Config:
        schema_extra = {
            "examples": [
                {"buzzword": "Synergy", "reasoning": "Often seen as a vague corporate cliché without specific meaning. Better to show synergy through concrete examples of collaboration."},
                {"buzzword": "Rockstar Developer", "reasoning": "Can be perceived as arrogant or unprofessional in some contexts. Focus on skills and achievements instead."}
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }

class BonusAddOnsOutput(BaseModel):
    template_suggestions: List[TemplateSuggestion] = Field(default_factory=list)
    buzzword_analysis_results: List[BuzzwordAnalysis] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "template_suggestions": [
                        {"template_name": "ResumeWorded ATS Template", "url": "https://www.resumeworded.com/resume-templates/", "description": "Offers various ATS-optimized templates."},
                        {"template_name": "Enhancv ATS-Friendly Templates", "url": "https://enhancv.com/resume-templates/ats-friendly/", "description": "Visually appealing yet ATS-compatible templates."}
                    ],
                    "buzzword_analysis_results": [
                        {"buzzword": "Guru", "reasoning": "Sounds informal and might not be taken seriously. 'Expert' or 'Specialist' is more professional."},
                        {"buzzword": "Disruptive Innovation", "reasoning": "Overused and often misapplied. Show, don't just tell, how your work was innovative."}
                    ]
                }
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }

class SmartFeedbackOutput(BaseModel):
    strong_points: List[str] = Field(..., description="Key strengths identified from the analysis.")
    areas_for_improvement: List[str] = Field(..., description="Key areas where the candidate can improve.")
    quick_wins: List[str] = Field(..., max_items=3, description="Up to 3 actionable quick wins the candidate can implement.")
    overall_advice: Optional[str] = Field(None, description="Overall summary advice or encouragement.")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "strong_points": ["Solid technical skills in Python and SQL.", "Good ATS compatibility score.", "Clear communication in project descriptions."],
                    "areas_for_improvement": ["Lack of demonstrated experience with specific cloud technologies (AWS, Kubernetes) mentioned in JD.", "Experience in leading large-scale AI projects needs to be better highlighted or acquired.", "Incorporate more keywords from JD like 'Terraform' and 'MLOps'."],
                    "quick_wins": ["Add a dedicated 'Cloud Skills' section to your resume, listing AWS and any related proficiencies.", "Quantify achievements in your 'Senior Software Engineer' role with specific metrics.", "Review the JD for keywords like 'Terraform' and 'MLOps' and see where they can be naturally integrated into your experience section."],
                    "overall_advice": "You have a strong foundation. Focusing on showcasing your cloud skills and leadership experience, while tailoring your resume with specific keywords, will significantly boost your chances."
                }
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }

class CoverLetterOutput(BaseModel):
    cover_letter_text: str = Field(..., description="The full generated text of the cover letter.")
    notes: Optional[str] = Field(None, description="Optional notes from the LLM regarding the cover letter generation, e.g., assumptions made or areas to customize further.")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "cover_letter_text": "Dear [Hiring Manager],\n\nI am writing to express my keen interest in the [Role Title] position at [Company Name] as advertised on [Platform]...",
                    "notes": "This cover letter is a general template. Consider adding specific anecdotes or tailoring the second paragraph to a unique company value if known."
                }
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }


class ResumeRewriteOutput(BaseModel):
    overall_summary: str = Field(..., description="A brief summary of changes made and their intent.")
    rewritten_headline: Optional[RewrittenSection] = None
    rewritten_summary: Optional[RewrittenSection] = None
    rewritten_experience_bullets: Optional[RewrittenSection] = None # Assuming one experience section targeted for now
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "overall_summary": "Rewrote headline, summary, and key experience bullets to better align with 'Senior AI Engineer' role, focusing on leadership, AI/ML skills, and cloud technologies.",
                    "rewritten_headline": {
                        "original_content": "Software Engineer",
                        "rewritten_content": "Senior Software Engineer | AI & Machine Learning Enthusiast | Cloud Proficient",
                        "attempted_keywords": ["AI", "Machine Learning", "Cloud", "Senior"]
                    },
                    "rewritten_summary": {
                        "original_content": "Experienced developer seeking new challenges.",
                        "rewritten_content": "Results-oriented Senior Software Engineer with 5+ years of experience in Python and a growing expertise in AI/ML development and cloud platforms (AWS). Eager to leverage these skills to drive innovation in AI-focused projects.",
                        "attempted_keywords": ["Senior Software Engineer", "AI/ML", "Python", "AWS", "innovation"]
                    }
                }
            ]
        }
        # For Pydantic V2 use model_config
        # model_config = { ... }


class RoleMismatchSignal(BaseModel):
    signal_type: str = Field(..., description="Type of mismatch, e.g., 'Overqualified', 'Underqualified', 'Different Career Trajectory'")
    reasoning: str = Field(..., description="Explanation for the identified mismatch signal")
    evidence: List[str] = Field(default_factory=list, description="Specific phrases or facts from resume/JD supporting this signal")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "signal_type": "Overqualified",
                    "reasoning": "Candidate has 15 years of experience and managed large teams, while the role is mid-level and primarily individual contributor.",
                    "evidence": ["Resume: 'Led department of 20 engineers'", "JD: '3-5 years experience required'"]
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "signal_type": "Overqualified",
        #                "reasoning": "Candidate has 15 years of experience and managed large teams, while the role is mid-level and primarily individual contributor.",
        #                "evidence": ["Resume: 'Led department of 20 engineers'", "JD: '3-5 years experience required'"]
        #            }
        #        ]
        #    }
        # }


class GapsOutput(BaseModel):
    experience_gaps: List[str] = Field(..., description="Significant experience gaps identified (e.g., missing years in specific domains required by JD)")
    qualification_gaps: List[str] = Field(..., description="Gaps in formal qualifications (e.g., certifications, degrees)")
    potential_mismatches: List[RoleMismatchSignal] = Field(default_factory=list, description="List of potential role mismatches detected")
    # Example for Pydantic V1
    class Config:
        schema_extra = {
            "examples": [
                {
                    "experience_gaps": ["Lacks experience in direct B2C product development.", "No explicit mention of managing budgets over $1M."],
                    "qualification_gaps": ["JD requires PMP certification, not listed in resume."],
                    "potential_mismatches": [
                        {
                            "signal_type": "Different Career Trajectory",
                            "reasoning": "Candidate's experience is heavily in academic research, while role is industry-focused product development.",
                            "evidence": ["Resume: 'Published 15+ papers'", "JD: 'Drive product to market'"]
                        }
                    ]
                }
            ]
        }
        # For Pydantic V2, use model_config
        # model_config = {
        #    "json_schema_extra": {
        #        "examples": [
        #            {
        #                "experience_gaps": ["Lacks experience in direct B2C product development.", "No explicit mention of managing budgets over $1M."],
        #                "qualification_gaps": ["JD requires PMP certification, not listed in resume."],
        #                "potential_mismatches": [
        #                    {
        #                        "signal_type": "Different Career Trajectory",
        #                        "reasoning": "Candidate's experience is heavily in academic research, while role is industry-focused product development.",
        #                        "evidence": ["Resume: 'Published 15+ papers'", "JD: 'Drive product to market'"]
        #                    }
        #                ]
        #            }
        #        ]
        #    }
        # }
