# eval_dataset.py - Ground truth Q&A dataset for evaluating AI quality
# These are real questions with expected answers we use to measure AI performance
# The more questions you add here, the better the evaluation becomes

EVAL_DATASET = [
    {
        "id": "q001",
        "category": "resume",
        "question": "How should I write my resume for a Python internship?",
        "expected_keywords": [
            "one page", "projects", "github", "skills", "python",
            "action verbs", "quantify", "tailored"
        ],
        "expected_topics": ["resume", "python internship"]
    },
    {
        "id": "q002",
        "category": "interview",
        "question": "How do I prepare for a technical internship interview?",
        "expected_keywords": [
            "leetcode", "data structures", "algorithms", "star method",
            "behavioral", "research", "practice", "company"
        ],
        "expected_topics": ["interview preparation"]
    },
    {
        "id": "q003",
        "category": "platforms",
        "question": "Where can I find internships in India?",
        "expected_keywords": [
            "linkedin", "internshala", "unstop", "angellist",
            "apply", "networking", "profile", "connect"
        ],
        "expected_topics": ["finding internships"]
    },
    {
        "id": "q004",
        "category": "skills",
        "question": "What skills do I need for a machine learning internship?",
        "expected_keywords": [
            "python", "numpy", "pandas", "scikit-learn",
            "tensorflow", "pytorch", "kaggle", "statistics"
        ],
        "expected_topics": ["machine learning internship"]
    },
    {
        "id": "q005",
        "category": "cover_letter",
        "question": "How do I write a good cover letter for an internship?",
        "expected_keywords": [
            "three paragraphs", "personalize", "skills", "project",
            "enthusiasm", "300 words", "company", "role"
        ],
        "expected_topics": ["cover letter"]
    },
    {
        "id": "q006",
        "category": "linkedin",
        "question": "How can I use LinkedIn to get an internship?",
        "expected_keywords": [
            "profile", "connect", "alumni", "recruiter",
            "message", "photo", "headline", "post"
        ],
        "expected_topics": ["networking and linkedin"]
    },
    {
        "id": "q007",
        "category": "skills",
        "question": "What skills do I need for a web development internship?",
        "expected_keywords": [
            "html", "css", "javascript", "react",
            "frontend", "backend", "git", "projects"
        ],
        "expected_topics": ["web development internship"]
    },
    {
        "id": "q008",
        "category": "learning",
        "question": "What are the best free resources to learn programming for internships?",
        "expected_keywords": [
            "freecodecamp", "coursera", "youtube", "github",
            "open source", "projects", "certification", "cs50"
        ],
        "expected_topics": ["skill development"]
    },
    {
        "id": "q009",
        "category": "data_science",
        "question": "How do I get a data science internship as a beginner?",
        "expected_keywords": [
            "python", "sql", "statistics", "kaggle",
            "portfolio", "visualization", "pandas", "projects"
        ],
        "expected_topics": ["data science internship"]
    },
    {
        "id": "q010",
        "category": "general",
        "question": "How many internship applications should I send per week?",
        "expected_keywords": [
            "apply", "consistent", "follow up", "personalize",
            "track", "quality", "tailored", "multiple"
        ],
        "expected_topics": ["finding internships"]
    }
]