# modules/jd_analyzer.py

import re
import spacy # type: ignore
from modules.resume_parser import SKILL_KEYWORDS

nlp = spacy.load("en_core_web_md")

# ─── SIGNALS ──────────────────────────────────────────────────────

REQUIRED_SIGNALS = [
    "required", "must have", "must-have", "mandatory", "essential",
    "you must", "we require", "need to have", "minimum requirement",
    "should have", "you should", "expected to", "responsible for",
    "key responsibilities", "responsibilities", "role requires",
    "will be responsible", "accountable for", "key skills",
    "must possess", "candidate must", "looking for",
]

PREFERRED_SIGNALS = [
    "preferred", "nice to have", "nice-to-have", "bonus", "plus",
    "advantageous", "desirable", "good to have", "familiarity with",
    "exposure to", "knowledge of", "would be a plus",
    "added advantage", "preferred qualifications",
]

# ─── SECTION DETECTION ────────────────────────────────────────────

JD_SECTIONS = {
    "requirements":     ["requirements", "required skills", "qualifications",
                         "what you need", "minimum qualifications",
                         "key skills", "must have", "you will need"],
    "preferred":        ["preferred", "nice to have", "bonus skills",
                         "good to have", "preferred qualifications"],
    "responsibilities": ["responsibilities", "key responsibilities",
                         "what you will do", "your role", "duties",
                         "role overview", "job responsibilities",
                         "you will be", "accountabilities"],
    "about":            ["about the role", "about us", "overview",
                         "job description", "role overview", "about"],
}


def detect_jd_sections(text):
    sections    = {key: "" for key in JD_SECTIONS}
    sections["other"] = ""
    lines       = text.splitlines()
    current_sec = "other"

    for line in lines:
        clean   = line.strip().lower()
        matched = False
        for sec, keywords in JD_SECTIONS.items():
            if any(clean.startswith(kw) for kw in keywords):
                current_sec = sec
                matched     = True
                break
        if not matched:
            sections[current_sec] += line + "\n"

    return sections


# ─── SKILL EXTRACTION ─────────────────────────────────────────────

def extract_skills_from_jd(text):
    found          = set()
    text_lower     = text.lower()
    text_normalized = re.sub(r'[-/]', ' ', text_lower)
    text_normalized = re.sub(r'\s+', ' ', text_normalized)

    for skill in SKILL_KEYWORDS:
        skill_normalized = re.sub(r'[-/]', ' ', skill)
        skill_normalized = re.sub(r'\s+', ' ', skill_normalized)

        if re.search(r'[^a-zA-Z0-9 ]', skill_normalized):
            if skill_normalized in text_normalized:
                found.add(skill)
        else:
            pattern = r'\b' + re.escape(skill_normalized) + r'\b'
            if re.search(pattern, text_normalized):
                found.add(skill)

    # spaCy NER
    doc = nlp(text[:50000])
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT"):
            candidate = ent.text.lower().strip()
            if candidate in SKILL_KEYWORDS:
                found.add(candidate)

    return found


# ─── CLASSIFY REQUIRED vs PREFERRED ──────────────────────────────

def classify_skills(text, all_skills, sections):
    required  = set()
    preferred = set()

    # Skills found in the preferred section → preferred
    preferred_section_text = re.sub(r'[-/]', ' ',
        sections.get("preferred", "").lower())

    # Skills found in responsibilities/requirements → required
    req_section_text = re.sub(r'[-/]', ' ', (
        sections.get("requirements", "") +
        sections.get("responsibilities", "") +
        sections.get("other", "")
    ).lower())

    lines = text.lower().splitlines()

    for skill in all_skills:
        skill_norm = re.sub(r'[-/]', ' ', skill)

        in_preferred_sec = bool(re.search(
            r'\b' + re.escape(skill_norm) + r'\b', preferred_section_text))
        in_required_sec  = bool(re.search(
            r'\b' + re.escape(skill_norm) + r'\b', req_section_text))

        # Check signal words around the skill in each line
        skill_required  = False
        skill_preferred = False

        for line in lines:
            line_norm = re.sub(r'[-/]', ' ', line)
            if not re.search(r'\b' + re.escape(skill_norm) + r'\b', line_norm):
                continue
            if any(sig in line_norm for sig in REQUIRED_SIGNALS):
                skill_required = True
            elif any(sig in line_norm for sig in PREFERRED_SIGNALS):
                skill_preferred = True

        # Priority: explicit signals > section placement > default required
        if skill_preferred and not skill_required and in_preferred_sec:
            preferred.add(skill)
        else:
            required.add(skill)

    return required, preferred


# ─── MAIN ANALYZER ────────────────────────────────────────────────

def analyze_jd(jd_text):
    print("\n[Analyzing JD]")

    if not jd_text.strip():
        print("  [ERROR] Empty JD text.")
        return None

    sections   = detect_jd_sections(jd_text)
    detected   = [s for s, t in sections.items() if t.strip()]
    print(f"  [OK] Sections found: {', '.join(detected)}")

    all_skills = extract_skills_from_jd(jd_text)
    print(f"  [OK] Total skills found: {len(all_skills)}")

    required, preferred = classify_skills(jd_text, all_skills, sections)
    print(f"  [OK] Required: {len(required)}  |  Preferred: {len(preferred)}")

    return {
        "raw_text":         jd_text,
        "sections":         sections,
        "all_skills":       sorted(all_skills),
        "required_skills":  sorted(required),
        "preferred_skills": sorted(preferred),
    }