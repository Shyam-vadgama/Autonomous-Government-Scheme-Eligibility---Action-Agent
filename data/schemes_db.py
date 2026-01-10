"""
Sample Government Schemes Database
Contains information about various Indian government schemes
"""

GOVERNMENT_SCHEMES = [
    {
        "scheme_id": "pmkisan_001",
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "category": "agriculture",
        "department": "Ministry of Agriculture & Farmers Welfare",
        "description": "Financial support to landholding farmer families",
        "benefits": {
            "amount": 6000,
            "frequency": "annual",
            "installments": 3,
            "per_installment": 2000
        },
        "eligibility_criteria": {
            "is_farmer": True,
            "land_ownership": True,
            "income_category": ["bpl", "apl"],
            "exclusions": ["income_tax_payers", "government_employees"]
        },
        "geographical_scope": "national",
        "target_groups": ["farmers", "landowners"],
        "documents_required": [
            "aadhaar_card", "bank_account", "land_records", "passport_photo"
        ],
        "application_process": "online_and_offline",
        "official_website": "https://pmkisan.gov.in",
        "launch_year": 2019,
        "status": "active"
    },
    
    {
        "scheme_id": "pmay_002",
        "name": "Pradhan Mantri Awas Yojana (PMAY)",
        "category": "housing",
        "department": "Ministry of Housing and Urban Affairs",
        "description": "Housing for all by providing affordable housing",
        "benefits": {
            "subsidy_amount": 267000,
            "loan_amount": 1200000,
            "interest_subsidy": "6.5%"
        },
        "eligibility_criteria": {
            "annual_income": {"max": 1800000},
            "first_time_buyer": True,
            "no_existing_house": True
        },
        "geographical_scope": "national",
        "target_groups": ["first_time_home_buyers", "middle_income"],
        "documents_required": [
            "aadhaar_card", "income_certificate", "bank_statement", "property_documents"
        ],
        "application_process": "online",
        "official_website": "https://pmaymis.gov.in",
        "launch_year": 2015,
        "status": "active"
    },
    
    {
        "scheme_id": "nrega_003",
        "name": "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)",
        "category": "employment",
        "department": "Ministry of Rural Development",
        "description": "100 days of guaranteed wage employment in rural areas",
        "benefits": {
            "guaranteed_days": 100,
            "daily_wage": 202,
            "maximum_annual": 20200
        },
        "eligibility_criteria": {
            "rural_urban": "rural",
            "age": {"min": 18},
            "willing_to_work": True
        },
        "geographical_scope": "rural_areas_only",
        "target_groups": ["rural_unemployed", "daily_wage_workers"],
        "documents_required": [
            "aadhaar_card", "job_card", "bank_account"
        ],
        "application_process": "offline_gram_panchayat",
        "official_website": "https://nrega.nic.in",
        "launch_year": 2005,
        "status": "active"
    },
    
    {
        "scheme_id": "janani_004",
        "name": "Janani Suraksha Yojana (JSY)",
        "category": "health_maternal",
        "department": "Ministry of Health and Family Welfare",
        "description": "Safe motherhood intervention to reduce maternal mortality",
        "benefits": {
            "rural_amount": 1400,
            "urban_amount": 1000,
            "additional_benefits": "free_delivery"
        },
        "eligibility_criteria": {
            "gender": "female",
            "is_pregnant_lactating": True,
            "income_category": ["bpl"],
            "institutional_delivery": True
        },
        "geographical_scope": "national",
        "target_groups": ["pregnant_women", "bpl_families"],
        "documents_required": [
            "aadhaar_card", "bpl_card", "pregnancy_certificate", "bank_account"
        ],
        "application_process": "hospital_anm",
        "official_website": "https://nhm.gov.in/index1.php?lang=1&level=2&sublinkid=841&lid=309",
        "launch_year": 2005,
        "status": "active"
    },
    
    {
        "scheme_id": "scholarship_005",
        "name": "Post Matric Scholarship for SC Students",
        "category": "education",
        "department": "Ministry of Social Justice and Empowerment",
        "description": "Financial assistance for SC students pursuing higher education",
        "benefits": {
            "maintenance_allowance": 1200,
            "tuition_fees": "full_coverage",
            "book_allowance": 3000
        },
        "eligibility_criteria": {
            "caste_category": "sc",
            "education_level": "post_matriculation",
            "family_income": {"max": 250000},
            "academic_performance": "pass_marks"
        },
        "geographical_scope": "national",
        "target_groups": ["sc_students", "higher_education"],
        "documents_required": [
            "caste_certificate", "income_certificate", "academic_certificates", "bank_account"
        ],
        "application_process": "online_scholarship_portal",
        "official_website": "https://scholarships.gov.in",
        "launch_year": 1944,
        "status": "active"
    },
    
    {
        "scheme_id": "pension_006",
        "name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "category": "social_security",
        "department": "Ministry of Rural Development",
        "description": "Pension support for elderly citizens",
        "benefits": {
            "monthly_pension": 200,
            "annual_amount": 2400,
            "additional_state_support": "varies"
        },
        "eligibility_criteria": {
            "age": {"min": 60},
            "income_category": ["bpl"],
            "no_government_pension": True
        },
        "geographical_scope": "national",
        "target_groups": ["senior_citizens", "bpl_families"],
        "documents_required": [
            "age_proof", "bpl_card", "bank_account", "aadhaar_card"
        ],
        "application_process": "panchayat_office",
        "official_website": "https://nsap.nic.in",
        "launch_year": 1995,
        "status": "active"
    },
    
    {
        "scheme_id": "disability_007",
        "name": "Indira Gandhi National Disability Pension Scheme (IGNDPS)",
        "category": "social_security",
        "department": "Ministry of Rural Development", 
        "description": "Pension for persons with severe/multiple disabilities",
        "benefits": {
            "monthly_pension": 300,
            "annual_amount": 3600
        },
        "eligibility_criteria": {
            "disability_status": True,
            "disability_percentage": {"min": 80},
            "age": {"min": 18, "max": 59},
            "income_category": ["bpl"]
        },
        "geographical_scope": "national",
        "target_groups": ["disabled_persons", "bpl_families"],
        "documents_required": [
            "disability_certificate", "bpl_card", "bank_account", "aadhaar_card"
        ],
        "application_process": "panchayat_office",
        "official_website": "https://nsap.nic.in",
        "launch_year": 2009,
        "status": "active"
    },
    
    {
        "scheme_id": "ration_008",
        "name": "National Food Security Act (NFSA) - Subsidized Food Grains",
        "category": "food_security",
        "department": "Ministry of Consumer Affairs, Food and Public Distribution",
        "description": "Subsidized food grains through Public Distribution System",
        "benefits": {
            "rice_price_per_kg": 3,
            "wheat_price_per_kg": 2,
            "coarse_grain_price_per_kg": 1,
            "monthly_allocation": "5kg_per_person"
        },
        "eligibility_criteria": {
            "income_category": ["bpl", "aay"],
            "valid_ration_card": True
        },
        "geographical_scope": "national",
        "target_groups": ["bpl_families", "aay_families"],
        "documents_required": [
            "ration_card", "aadhaar_card", "income_proof"
        ],
        "application_process": "fair_price_shop",
        "official_website": "https://dfpd.gov.in",
        "launch_year": 2013,
        "status": "active"
    }
]