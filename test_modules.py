# tests/test_modules.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.resume_parser import extract_skills_from_text
from modules.jd_analyzer   import extract_skills_from_jd, classify_skills
from modules.gap_analyzer  import analyze_gaps

# ─── RESUME PARSER TESTS ──────────────────────────────────────────

def test_basic_skill_extraction():
    text = "Proficient in Python, SQL and machine learning."
    skills = extract_skills_from_text(text)
    assert "python"          in skills
    assert "sql"             in skills
    assert "machine learning" in skills

def test_cpp_extraction():
    text = "Experience with C++ and Java development."
    skills = extract_skills_from_text(text)
    assert "c++" in skills

def test_hyphen_normalization():
    text = "Strong problem-solving and critical thinking skills."
    skills = extract_skills_from_text(text)
    assert "problem solving" in skills

def test_empty_text():
    skills = extract_skills_from_text("")
    assert skills == []

# ─── JD ANALYZER TESTS ────────────────────────────────────────────

def test_jd_required_classification():
    jd = "Python is required. Experience with Docker is preferred."
    skills = extract_skills_from_jd(jd)
    required, preferred = classify_skills(jd, skills)
    assert "python" in required
    assert "docker" in preferred

def test_jd_no_signals():
    jd = "We need Python and SQL for this role."
    skills = extract_skills_from_jd(jd)
    required, preferred = classify_skills(jd, skills)
    # No signal = defaults to required
    assert "python" in required
    assert "sql"    in required

# ─── GAP ANALYZER TESTS ───────────────────────────────────────────

def test_perfect_match():
    resume   = ["python", "sql", "machine learning"]
    required = ["python", "sql", "machine learning"]
    preferred = []
    result = analyze_gaps(resume, required, preferred)
    assert result["match_score"] == 100.0
    assert len(result["critical_gaps"]) == 0

def test_zero_match():
    resume    = ["html", "css"]
    required  = ["python", "sql", "machine learning"]
    preferred = []
    result = analyze_gaps(resume, required, preferred)
    assert result["match_score"] == 0.0
    assert len(result["critical_gaps"]) == 3

def test_partial_match():
    resume    = ["python", "html"]
    required  = ["python", "sql", "machine learning"]
    preferred = ["docker"]
    result = analyze_gaps(resume, required, preferred)
    assert 0 < result["match_score"] < 100
    assert "sql"             in result["critical_gaps"]
    assert "machine learning" in result["critical_gaps"]
    assert "docker"          in result["minor_gaps"]

def test_recommendations_present():
    resume    = []
    required  = ["python", "sql"]
    preferred = []
    result = analyze_gaps(resume, required, preferred)
    for skill in result["critical_gaps"]:
        assert skill in result["recommendations"]