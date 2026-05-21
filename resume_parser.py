# modules/resume_parser.py

import re
import spacy # type: ignore
import PyPDF2 # type: ignore
from pdfminer.high_level import extract_text as pdfminer_extract # type: ignore

nlp = spacy.load("en_core_web_md")

# ─── UNIVERSAL SKILL TAXONOMY ─────────────────────────────────────

SKILL_KEYWORDS = {
    # ── Programming & Tech ──────────────────────────────────────
    "python", "java", "c++", "c", "c#", "javascript", "typescript",
    "r", "go", "golang", "rust", "swift", "kotlin", "php", "ruby",
    "scala", "matlab", "perl", "bash", "shell", "html", "css",

    # ── Frameworks & Tools ───────────────────────────────────────
    "react", "angular", "vue", "django", "flask", "fastapi", "spring",
    "node.js", "nodejs", "express", "bootstrap", "jquery", "next.js",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "opencv", "docker", "kubernetes", "git", "github", "gitlab",
    "aws", "azure", "gcp", "linux", "jenkins", "sql", "mysql",
    "postgresql", "mongodb", "sqlite", "redis", "excel", "tableau",
    "power bi", "jira", "figma", "jupyter", "hadoop", "spark", "kafka",

    # ── AI / Data ────────────────────────────────────────────────
    "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision", "data science",
    "data analysis", "data mining", "data visualization",
    "statistical analysis", "predictive modeling", "big data",

    # ── Sales & Business Development ─────────────────────────────
    "sales", "b2b sales", "b2c sales", "retail sales", "direct sales",
    "inside sales", "outside sales", "field sales", "channel sales",
    "institutional sales", "corporate sales", "sales planning",
    "sales strategy", "sales forecasting", "sales management",
    "business development", "business planning", "revenue generation",
    "lead generation", "lead management", "pipeline management",
    "deal closure", "upselling", "cross selling", "target achievement",
    "quota management", "market penetration", "volume growth",
    "product mix", "market share", "go to market",

    # ── Marketing ────────────────────────────────────────────────
    "marketing", "digital marketing", "content marketing",
    "social media marketing", "email marketing", "seo", "sem",
    "brand management", "market research", "market analysis",
    "competitive analysis", "campaign management", "promotions",
    "sales promotion", "advertising", "product marketing",
    "marketing strategy", "crm marketing",

    # ── Operations & Management ───────────────────────────────────
    "operations management", "operations", "process improvement",
    "process optimization", "project management", "program management",
    "portfolio management", "strategic planning", "business strategy",
    "change management", "risk management", "quality management",
    "supply chain management", "logistics", "inventory management",
    "vendor management", "procurement", "resource allocation",
    "cost management", "cost optimization", "budget management",
    "p&l management", "profit and loss", "financial planning",

    # ── Client & Customer ─────────────────────────────────────────
    "client servicing", "client management", "client retention",
    "customer relationship management", "crm", "customer service",
    "customer success", "customer acquisition", "customer retention",
    "account management", "key account management", "relationship management",
    "stakeholder management", "partner management",

    # ── Team & Leadership ─────────────────────────────────────────
    "team management", "team leadership", "people management",
    "leadership", "mentoring", "coaching", "performance management",
    "talent management", "hiring", "recruitment",

    # ── Finance & Banking ─────────────────────────────────────────
    "financial analysis", "financial modeling", "financial reporting",
    "accounting", "auditing", "taxation", "compliance",
    "delinquency management", "credit analysis", "risk assessment",
    "loan management", "collections", "banking", "insurance",
    "investment", "portfolio analysis", "wealth management",

    # ── Network & Distribution ───────────────────────────────────
    "dealer management", "dealer network", "distribution management",
    "channel management", "network expansion", "territory management",
    "zone management", "franchise management",

    # ── Analytical & Strategic ───────────────────────────────────
    "analytical skills", "analytical thinking", "problem solving",
    "critical thinking", "decision making", "strategic thinking",
    "business acumen", "commercial acumen", "market study",
    "trend analysis", "competitor analysis", "data driven",
    "reporting", "mis reporting", "dashboard reporting",

    # ── Communication & Interpersonal ────────────────────────────
    "communication", "presentation skills", "negotiation",
    "persuasion", "interpersonal skills", "public speaking",
    "written communication", "verbal communication",
    "cross functional collaboration", "collaboration", "teamwork",

    # ── Soft Skills ───────────────────────────────────────────────
    "time management", "organization", "multitasking",
    "attention to detail", "adaptability", "self motivated",
    "self drive", "enthusiasm", "initiative", "ownership",
    "accountability", "integrity", "work ethic", "resilience",

    # ── Healthcare ────────────────────────────────────────────────
    "clinical research", "patient care", "medical terminology",
    "healthcare management", "pharmaceutical", "drug development",
    "diagnosis", "treatment planning",

    # ── Legal ─────────────────────────────────────────────────────
    "legal research", "contract management", "intellectual property",
    "regulatory compliance", "litigation", "corporate law",

    # ── HR ────────────────────────────────────────────────────────
    "human resources", "hr management", "payroll", "onboarding",
    "employee relations", "learning and development", "training",

    # ── Education ─────────────────────────────────────────────────
    "curriculum development", "teaching", "instructional design",
    "e-learning", "assessment", "academic research",
}

# ─── TEXT EXTRACTION ──────────────────────────────────────────────

def extract_text_pypdf2(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"  [PyPDF2 error] {e}")
    return text.strip()


def extract_text_pdfminer(pdf_path):
    try:
        return pdfminer_extract(pdf_path).strip()
    except Exception as e:
        print(f"  [pdfminer error] {e}")
        return ""


def extract_text(pdf_path):
    text = extract_text_pypdf2(pdf_path)
    if len(text) < 100:
        print("  [info] PyPDF2 gave little text, trying pdfminer...")
        text = extract_text_pdfminer(pdf_path)
    return text


# ─── SECTION DETECTION ────────────────────────────────────────────

SECTION_HEADERS = {
    "skills":     ["skills", "technical skills", "core competencies",
                   "technologies", "tools", "expertise", "key skills",
                   "competencies", "proficiencies", "areas of expertise"],
    "experience": ["experience", "work experience", "employment",
                   "professional experience", "career history",
                   "work history", "internship"],
    "education":  ["education", "academic", "qualifications",
                   "degrees", "certifications", "courses", "training"],
    "projects":   ["projects", "personal projects", "academic projects",
                   "portfolio", "works", "achievements"],
    "summary":    ["summary", "objective", "profile", "about",
                   "professional summary", "career objective"],
}


def detect_sections(text):
    sections    = {key: "" for key in SECTION_HEADERS}
    sections["other"] = ""
    lines       = text.splitlines()
    current_sec = "other"

    for line in lines:
        clean   = line.strip().lower()
        matched = False
        for sec, keywords in SECTION_HEADERS.items():
            if any(clean == kw or clean.startswith(kw) for kw in keywords):
                current_sec = sec
                matched     = True
                break
        if not matched:
            sections[current_sec] += line + "\n"

    return sections


# ─── SKILL EXTRACTION ─────────────────────────────────────────────

def extract_skills_from_text(text):
    """Extract skills using keyword matching + spaCy NER."""
    if not text:
        return []

    found          = set()
    text_lower     = text.lower()
    text_normalized = re.sub(r'[-/]', ' ', text_lower)
    text_normalized = re.sub(r'\s+', ' ', text_normalized)

    for skill in SKILL_KEYWORDS:
        skill_normalized = re.sub(r'[-/]', ' ', skill)
        skill_normalized = re.sub(r'\s+', ' ', skill_normalized)

        # Special chars (c++, c#, p&l) — direct substring search
        if re.search(r'[^a-zA-Z0-9 ]', skill_normalized):
            if skill_normalized in text_normalized:
                found.add(skill)
        else:
            pattern = r'\b' + re.escape(skill_normalized) + r'\b'
            if re.search(pattern, text_normalized):
                found.add(skill)

    # spaCy NER
    doc = nlp(text[:50000])  # limit for performance
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "GPE"):
            candidate = ent.text.lower().strip()
            if candidate in SKILL_KEYWORDS:
                found.add(candidate)

    return sorted(found)


# ─── MAIN PARSER ──────────────────────────────────────────────────

def parse_resume(pdf_path):
    print(f"\n[Parsing] {pdf_path}")

    raw_text = extract_text(pdf_path)
    if not raw_text:
        print("  [ERROR] Could not extract text from PDF.")
        return None

    print(f"  [OK] Extracted {len(raw_text)} characters")

    sections = detect_sections(raw_text)
    detected = [s for s, t in sections.items() if t.strip()]
    print(f"  [OK] Sections found: {', '.join(detected)}")

    skills_text = raw_text + "\n" + sections.get("skills", "")
    skills      = extract_skills_from_text(skills_text)
    print(f"  [OK] Skills extracted: {len(skills)} skills found")

    return {
        "raw_text": raw_text,
        "sections": sections,
        "skills":   skills,
    }