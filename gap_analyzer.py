# modules/gap_analyzer.py

import re
import spacy # type: ignore

nlp = spacy.load("en_core_web_md")

# ─── RECOMMENDATIONS ──────────────────────────────────────────────

RECOMMENDATIONS = {
    # ── Programming & Tech ────────────────────────────────────────
    "python":           "Course: 'Python for Everybody' — coursera.org/specializations/python",
    "java":             "Course: 'Java Programming' by Duke University — coursera.org/learn/duke-programming-web",
    "c++":              "Course: 'C++ For C Programmers' — coursera.org/learn/c-plus-plus-a",
    "javascript":       "Course: 'JavaScript Algorithms' — freecodecamp.org/learn/javascript-algorithms-and-data-structures",
    "sql":              "Course: 'SQL for Data Science' — coursera.org/learn/sql-for-data-science | Practice: sqlzoo.net",
    "html":             "Course: 'Responsive Web Design' — freecodecamp.org/learn/2022/responsive-web-design",
    "css":              "Course: 'CSS — The Complete Guide' — udemy.com/course/css-the-complete-guide-incl-flexbox-grid-sass",
    "git":              "Course: 'Version Control with Git' — coursera.org/learn/version-control-with-git | Practice: learngitbranching.js.org",
    "docker":           "Course: 'Docker for Beginners' — docker.com/101-tutorial | Full: udemy.com/course/docker-mastery",
    "aws":              "Course: 'AWS Cloud Practitioner Essentials' — aws.amazon.com/training/learn-about/cloud-practitioner",
    "machine learning": "Course: 'Machine Learning Specialization' by Andrew Ng — coursera.org/specializations/machine-learning-introduction",
    "deep learning":    "Course: 'Deep Learning Specialization' by Andrew Ng — coursera.org/specializations/deep-learning",
    "nlp":              "Course: 'Natural Language Processing Specialization' — coursera.org/specializations/natural-language-processing",
    "data science":     "Course: 'IBM Data Science Professional Certificate' — coursera.org/professional-certificates/ibm-data-science",
    "data analysis":    "Course: 'Data Analysis with Python' — coursera.org/learn/data-analysis-with-python | freecodecamp.org",
    "tensorflow":       "Course: 'TensorFlow Developer Certificate' — coursera.org/professional-certificates/tensorflow-in-practice",
    "pytorch":          "Tutorial: Official PyTorch tutorials — pytorch.org/tutorials",
    "tableau":          "Course: 'Tableau Training for Beginners' — tableau.com/learn/training | udemy.com/course/tableau10",
    "power bi":         "Course: Microsoft 'Power BI' learning path — learn.microsoft.com/en-us/training/powerplatform/power-bi",
    "flask":            "Tutorial: 'Flask Mega-Tutorial' by Miguel Grinberg — blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world",
    "kubernetes":       "Course: 'Kubernetes for the Absolute Beginner' — udemy.com/course/learn-kubernetes",
    "azure":            "Course: 'Microsoft Azure Fundamentals AZ-900' — learn.microsoft.com/en-us/certifications/azure-fundamentals",

    # ── Sales ─────────────────────────────────────────────────────
    "sales":                "Course: 'Sales Training: Practical Sales Techniques' — udemy.com/course/sales-training-practical-sales-techniques | Book: 'The Challenger Sale' by Dixon & Adamson",
    "b2b sales":            "Course: 'B2B Sales Masterclass' — udemy.com/course/b2b-sales | Free: HubSpot Academy 'Sales Enablement' — academy.hubspot.com",
    "b2c sales":            "Course: 'Retail Sales Techniques' — linkedin.com/learning/retail-sales-foundations | Book: 'To Sell Is Human' by Daniel Pink",
    "retail sales":         "Course: 'Retail Sales Foundations' — linkedin.com/learning/retail-sales-foundations | NRF Retail Certification: nrf.com/resources/for-students",
    "institutional sales":  "Course: 'Enterprise Sales' on LinkedIn Learning — linkedin.com/learning/topics/enterprise-sales | Book: 'SPIN Selling' by Neil Rackham",
    "corporate sales":      "Course: 'Corporate Sales Strategy' — linkedin.com/learning/sales-strategy-foundations | Book: 'The New Strategic Selling' by Miller & Heiman",
    "sales planning":       "Course: 'Sales Management Foundations' — linkedin.com/learning/sales-management-foundations | Salesforce Trailhead: trailhead.salesforce.com",
    "sales strategy":       "Course: 'Sales Strategy' by Northwestern — coursera.org/learn/sales-strategy | Book: 'New Sales. Simplified.' by Mike Weinberg",
    "sales forecasting":    "Course: 'Forecasting Models' — coursera.org/learn/financial-modeling | Tool training: Salesforce Trailhead — trailhead.salesforce.com",
    "sales management":     "Course: 'Sales Management' — linkedin.com/learning/sales-management-foundations | Certification: Salesforce Sales Operations — trailhead.salesforce.com",
    "lead generation":      "Course: 'Inbound Marketing Certification' — academy.hubspot.com/courses/inbound-marketing | Free: HubSpot Academy",
    "pipeline management":  "Course: 'Sales Pipeline Management' — linkedin.com/learning/sales-pipeline-management | Tool: HubSpot CRM free — hubspot.com/crm",
    "target achievement":   "Course: 'Goal Setting and Achievement' — coursera.org/learn/goal-setting | Book: 'The 4 Disciplines of Execution' by McChesney & Covey",
    "volume growth":        "Course: 'Revenue Operations' — linkedin.com/learning/revenue-operations-foundations | Book: 'Predictable Revenue' by Aaron Ross",
    "market penetration":   "Course: 'Marketing Strategy' by Coursera — coursera.org/learn/marketing-strategy | Book: 'Blue Ocean Strategy' by Kim & Mauborgne",
    "market share":         "Course: 'Competitive Strategy' — coursera.org/learn/competitive-strategy | Book: 'Competitive Advantage' by Michael Porter",
    "product mix":          "Course: 'Product Management Fundamentals' — linkedin.com/learning/product-management-foundations | Book: 'Inspired' by Marty Cagan",
    "upselling":            "Course: 'Upselling Techniques' — linkedin.com/learning/upselling-techniques | Free: HubSpot Academy Sales courses — academy.hubspot.com",
    "cross selling":        "Course: 'Cross-Selling Strategies' — linkedin.com/learning/cross-selling-strategies | Book: 'Never Lose a Customer Again' by Joey Coleman",
    "deal closure":         "Course: 'Closing Techniques' — udemy.com/course/sales-training-practical-sales-techniques | Book: 'The Art of Closing the Sale' by Brian Tracy",

    # ── Business Development ──────────────────────────────────────
    "business development": "Course: 'Business Development Foundations' — linkedin.com/learning/business-development-foundations | Book: 'The New Business Road Test' by John Mullins",
    "business planning":    "Course: 'Business Plan Writing' — coursera.org/learn/how-to-write-a-business-plan | Free: SBA Business Planning Guide — sba.gov",
    "revenue generation":   "Course: 'Revenue Management' — coursera.org/learn/revenue-management | Book: 'Predictable Revenue' by Aaron Ross",
    "go to market":         "Course: 'Go-to-Market Strategy' — linkedin.com/learning/go-to-market-strategy | Book: 'Obviously Awesome' by April Dunford",

    # ── Marketing ─────────────────────────────────────────────────
    "marketing":            "Course: 'Foundations of Digital Marketing' by Google — skillshop.google.com | Free: HubSpot Marketing Certification — academy.hubspot.com",
    "digital marketing":    "Certification: 'Google Digital Marketing' — skillshop.google.com | Course: 'Digital Marketing Specialization' — coursera.org/specializations/digital-marketing",
    "market research":      "Course: 'Market Research and Consumer Behavior' — coursera.org/learn/market-research | Book: 'The Lean Startup' by Eric Ries",
    "competitive analysis": "Course: 'Competitive Strategy' — coursera.org/learn/competitive-strategy | Framework: Porter's Five Forces — isc.hbs.edu",
    "brand management":     "Course: 'Brand Management' by London Business School — coursera.org/learn/brand-management | Book: 'Building Strong Brands' by David Aaker",
    "campaign management":  "Course: 'Campaign Management' — linkedin.com/learning/marketing-campaign-management | Free: Google Ads certification — skillshop.google.com",
    "sales promotion":      "Course: 'Marketing Communications' — coursera.org/learn/marketing-communications | Book: 'Influence: The Psychology of Persuasion' by Robert Cialdini",
    "trend analysis":       "Course: 'Business Analytics' — coursera.org/learn/business-analytics | Tool: Google Trends — trends.google.com",

    # ── Operations & Management ───────────────────────────────────
    "operations management":  "Course: 'Operations Management' by Univ. of Illinois — coursera.org/learn/operations-management | Certification: APICS CPIM — apics.org",
    "operations":             "Course: 'Business Operations Management' — linkedin.com/learning/operations-management-foundations | Book: 'The Goal' by Eliyahu Goldratt",
    "project management":     "Certification: 'Google Project Management Certificate' — coursera.org/professional-certificates/google-project-management | PMP: pmi.org",
    "strategic planning":     "Course: 'Strategic Planning Foundation' — linkedin.com/learning/strategic-planning-foundations | Book: 'Good Strategy Bad Strategy' by Richard Rumelt",
    "cost management":        "Course: 'Finance for Non-Finance Managers' — coursera.org/learn/finance-for-non-finance-managers | Book: 'Cost Accounting' by Horngren",
    "budget management":      "Course: 'Budgeting and Finance' — linkedin.com/learning/finance-foundations-budgets | Free: Accounting Basics — khanacademy.org/economics-finance-domain",
    "risk management":        "Certification: 'PMI Risk Management Professional (PMI-RMP)' — pmi.org/certifications/risk-management-rmp | Course: coursera.org/learn/risk-management",
    "quality management":     "Certification: 'Six Sigma Green Belt' — asq.org/cert/six-sigma-green-belt | Course: 'Quality Management' — coursera.org/learn/quality-management",
    "change management":      "Certification: 'Prosci Change Management' — prosci.com/certification | Course: coursera.org/learn/change-management",
    "p&l management":         "Course: 'Financial Accounting' by Wharton — coursera.org/learn/wharton-accounting | Book: 'Financial Intelligence' by Berman & Knight",
    "profit and loss":        "Course: 'Understanding Financial Statements' — linkedin.com/learning/finance-foundations | Free: Khan Academy Finance — khanacademy.org",
    "vendor management":      "Course: 'Supply Chain Management' — coursera.org/specializations/supply-chain-management | LinkedIn Learning: linkedin.com/learning/topics/vendor-management",
    "supply chain management":"Certification: 'APICS CSCP' — apics.org/credentials-certifications/cscp | Course: coursera.org/specializations/supply-chain-management",

    # ── Client & Customer ─────────────────────────────────────────
    "client servicing":       "Course: 'Customer Service Foundations' — linkedin.com/learning/customer-service-foundations | Free: HubSpot 'Customer Service' — academy.hubspot.com",
    "client management":      "Course: 'Managing Client Relationships' — linkedin.com/learning/client-relations-foundations | Book: 'Never Lose a Customer Again' by Joey Coleman",
    "customer relationship management": "Course: 'CRM Fundamentals' — trailhead.salesforce.com | Free: HubSpot CRM Training — academy.hubspot.com",
    "crm":                    "Certification: 'Salesforce Admin Certification' — trailhead.salesforce.com | Free: HubSpot CRM — academy.hubspot.com",
    "customer service":       "Course: 'Customer Service Fundamentals' — coursera.org/learn/customer-service-fundamentals | Free: Google certificate — grow.google",
    "account management":     "Course: 'Key Account Management' — linkedin.com/learning/key-account-management | Book: 'The Challenger Customer' by Brent Adamson",
    "key account management": "Course: 'Strategic Account Management' — linkedin.com/learning/strategic-account-management | Certification: SAMA — strategicaccounts.org",
    "stakeholder management": "Course: 'Stakeholder Management' — linkedin.com/learning/stakeholder-management | PMI training: pmi.org/learning",
    "relationship management":"Course: 'Building Professional Relationships' — linkedin.com/learning/building-professional-relationships | Book: 'Never Eat Alone' by Keith Ferrazzi",

    # ── Team & Leadership ─────────────────────────────────────────
    "team management":        "Course: 'Managing People' by Univ. of London — coursera.org/learn/management-people | Book: 'The Making of a Manager' by Julie Zhuo",
    "leadership":             "Course: 'Everyday Leadership' by Duke — coursera.org/learn/everyday-leadership | Book: 'Leaders Eat Last' by Simon Sinek",
    "people management":      "Course: 'People Management Skills' — linkedin.com/learning/people-management-foundations | Book: 'First, Break All the Rules' by Buckingham",
    "mentoring":              "Course: 'Coaching and Mentoring' — linkedin.com/learning/coaching-and-mentoring | Book: 'The Coaching Habit' by Michael Bungay Stanier",
    "performance management": "Course: 'Performance Management' — linkedin.com/learning/performance-management-foundations | Book: 'Measure What Matters' by John Doerr",

    # ── Network & Distribution ───────────────────────────────────
    "dealer management":      "Course: 'Channel Sales Management' — linkedin.com/learning/channel-sales-foundations | Book: 'Channel Advantage' by Lawrence Friedman",
    "dealer network":         "Course: 'Distribution Channel Management' — linkedin.com/learning/channel-sales-foundations | Book: 'Managing Distribution Channels' by Julian Dent",
    "distribution management":"Course: 'Supply Chain & Distribution' — coursera.org/learn/supply-chain-logistics | Book: 'Distribution Channels' by Julian Dent",
    "channel management":     "Course: 'Channel Management and Retailing' — coursera.org/learn/channel-management | Certification: linkedin.com/learning/channel-sales-foundations",
    "network expansion":      "Course: 'Business Networking' — linkedin.com/learning/business-networking-foundations | Book: 'Never Eat Alone' by Keith Ferrazzi",
    "territory management":   "Course: 'Territory Sales Management' — linkedin.com/learning/territory-sales-management | Book: 'The Territory Management Handbook'",

    # ── Finance & Banking ─────────────────────────────────────────
    "financial analysis":     "Course: 'Financial Analysis for Decision Making' — edx.org/course/financial-analysis | Certification: CFA Institute — cfainstitute.org",
    "financial modeling":     "Course: 'Financial Modeling & Valuation' — corporatefinanceinstitute.com/courses/financial-modeling | udemy.com/course/financial-modeling",
    "delinquency management": "Course: 'Credit Risk Management' — coursera.org/learn/credit-risk-management | Certification: CAIIB — iibf.org.in",
    "credit analysis":        "Course: 'Credit Analysis' by CFI — corporatefinanceinstitute.com/courses/credit-analysis | Certification: CAIIB — iibf.org.in",
    "risk assessment":        "Course: 'Risk Assessment' — coursera.org/learn/risk-management | Book: 'Against the Gods: The Remarkable Story of Risk' by Peter Bernstein",
    "banking":                "Certification: 'JAIIB/CAIIB' — iibf.org.in | Course: 'Banking Fundamentals' — linkedin.com/learning/banking-foundations",
    "compliance":             "Course: 'Regulatory Compliance' — linkedin.com/learning/compliance-foundations | Certification: CRCM — aba.com/training-events/certifications",

    # ── Analytical & Soft Skills ─────────────────────────────────
    "analytical skills":      "Course: 'Critical Thinking & Problem Solving' by Rochester — coursera.org/learn/critical-thinking-problem-solving | Book: 'Thinking, Fast and Slow' by Kahneman",
    "analytical thinking":    "Course: 'Data-Driven Decision Making' — coursera.org/learn/decision-making | Book: 'Superforecasting' by Philip Tetlock",
    "problem solving":        "Course: 'Creative Problem Solving' — coursera.org/learn/creative-problem-solving | Book: 'The Art of Problem Solving' by Russell Ackoff",
    "critical thinking":      "Course: 'Critical Thinking' by Duke — coursera.org/learn/skeptical-thinking | Book: 'Asking the Right Questions' by Browne & Keeley",
    "decision making":        "Course: 'Decision Making and Scenarios' — coursera.org/learn/decision-making | Book: 'Decisive' by Chip & Dan Heath",
    "business acumen":        "Course: 'Business Fundamentals' — linkedin.com/learning/business-acumen-foundations | Book: 'The Ten-Day MBA' by Steven Silbiger",
    "commercial acumen":      "Course: 'Commercial Awareness' — linkedin.com/learning/commercial-awareness-foundations | Book: 'The McKinsey Way' by Ethan Rasiel",
    "market study":           "Course: 'Market Research' by UC Davis — coursera.org/learn/market-research | Tool: Statista — statista.com",
    "reporting":              "Course: 'Business Reporting' — linkedin.com/learning/business-reporting | Tool: Power BI training — learn.microsoft.com/power-bi",
    "mis reporting":          "Course: 'Management Information Systems' — coursera.org/learn/mis | Tool: Excel Advanced — linkedin.com/learning/excel-advanced",
    "data driven":            "Course: 'Data-Driven Decision Making' — coursera.org/learn/data-decision-making | Book: 'Competing on Analytics' by Davenport & Harris",

    # ── Communication & Interpersonal ────────────────────────────
    "communication":          "Course: 'Improving Communication Skills' by UPenn — coursera.org/learn/wharton-communication-skills | Book: 'Crucial Conversations' by Patterson et al.",
    "presentation skills":    "Course: 'Dynamic Public Speaking' by Univ. of Washington — coursera.org/specializations/public-speaking | Practice: Toastmasters — toastmasters.org",
    "negotiation":            "Course: 'Successful Negotiation' by Univ. of Michigan — coursera.org/learn/negotiation | Book: 'Never Split the Difference' by Chris Voss",
    "persuasion":             "Course: 'The Science of Persuasion' — linkedin.com/learning/persuasion-in-business | Book: 'Influence' by Robert Cialdini",
    "interpersonal skills":   "Course: 'Interpersonal Skills' — linkedin.com/learning/interpersonal-communication | Book: 'How to Win Friends and Influence People' by Dale Carnegie",
    "written communication":  "Course: 'Writing Skills for Engineering Leaders' — coursera.org/learn/engineering-writing | Book: 'On Writing Well' by William Zinsser",

    # ── Soft Skills ───────────────────────────────────────────────
    "self drive":             "Book: 'Drive: The Surprising Truth About What Motivates Us' by Daniel Pink | Course: 'Finding Purpose and Meaning at Work' — linkedin.com/learning",
    "self motivated":         "Course: 'Self-Motivation' — linkedin.com/learning/self-motivation | Book: 'Atomic Habits' by James Clear",
    "time management":        "Course: 'Work Smarter, Not Harder' by UC San Diego — coursera.org/learn/work-smarter | Book: 'Getting Things Done' by David Allen",
    "teamwork":               "Course: 'Teamwork Skills: Communicating Effectively' — coursera.org/learn/teamwork-skills | Book: 'The Five Dysfunctions of a Team' by Patrick Lencioni",
    "collaboration":          "Course: 'Collaboration Principles and Process' — linkedin.com/learning/collaboration-principles-and-process | Free: Google Workspace training",
    "adaptability":           "Course: 'Adaptability and Resiliency' — linkedin.com/learning/adaptability-and-resiliency | Book: 'Who Moved My Cheese?' by Spencer Johnson",
    "ownership":              "Course: 'Taking Initiative' — linkedin.com/learning/taking-initiative | Book: 'Extreme Ownership' by Jocko Willink",
    "attention to detail":    "Course: 'Improving Your Focus' — linkedin.com/learning/improving-your-focus | Practice through structured QA exercises",
    "enthusiasm":             "Book: 'The Power of Positive Thinking' by Norman Vincent Peale | Course: 'Positive Psychology' by UPenn — coursera.org/learn/positive-psychology",
}

DEFAULT_REC = "Search: '{skill}' courses on coursera.org, linkedin.com/learning, or udemy.com"


# ─── SEMANTIC SIMILARITY ──────────────────────────────────────────

def semantic_similarity(skill1, skill2):
    try:
        d1 = nlp(skill1)
        d2 = nlp(skill2)
        if d1.vector_norm and d2.vector_norm:
            return d1.similarity(d2)
    except Exception:
        pass
    return 0.0


def fuzzy_match(resume_skill, jd_skill, threshold=0.72):
    """Check if two skills are semantically similar enough."""
    # Exact match
    if resume_skill == jd_skill:
        return True, 1.0
    # One contains the other
    if resume_skill in jd_skill or jd_skill in resume_skill:
        return True, 0.9
    # Semantic similarity
    sim = semantic_similarity(resume_skill, jd_skill)
    if sim >= threshold:
        return True, sim
    return False, sim


# ─── MAIN GAP ANALYZER ────────────────────────────────────────────

def analyze_gaps(resume_skills, required_skills, preferred_skills):
    print("\n[Analyzing Gaps]")

    resume_set   = set(resume_skills)
    matched_req  = []
    matched_pref = []
    critical     = []
    minor        = []

    # ── Match required skills ─────────────────────────────────────
    for jd_skill in required_skills:
        best_match  = None
        best_score  = 0.0
        best_exact  = False

        for r_skill in resume_set:
            matched, score = fuzzy_match(r_skill, jd_skill)
            if matched and score > best_score:
                best_match = r_skill
                best_score = score
                best_exact = (score == 1.0)

        if best_match:
            matched_req.append({
                "skill":      jd_skill,
                "matched_by": best_match,
                "exact":      best_exact,
                "score":      round(best_score, 2),
            })
        else:
            critical.append({
                "skill":          jd_skill,
                "type":           "required",
                "severity":       "critical",
                "recommendation": RECOMMENDATIONS.get(jd_skill, DEFAULT_REC),
            })

    # ── Match preferred skills ────────────────────────────────────
    for jd_skill in preferred_skills:
        best_match = None
        best_score = 0.0
        best_exact = False

        for r_skill in resume_set:
            matched, score = fuzzy_match(r_skill, jd_skill)
            if matched and score > best_score:
                best_match = r_skill
                best_score = score
                best_exact = (score == 1.0)

        if best_match:
            matched_pref.append({
                "skill":      jd_skill,
                "matched_by": best_match,
                "exact":      best_exact,
                "score":      round(best_score, 2),
            })
        else:
            minor.append({
                "skill":          jd_skill,
                "type":           "preferred",
                "severity":       "minor",
                "recommendation": RECOMMENDATIONS.get(jd_skill, DEFAULT_REC.format(skill=jd_skill)),
            })

    # ── Score calculation ─────────────────────────────────────────
    total_req  = len(required_skills)
    total_pref = len(preferred_skills)

    if total_req > 0 and total_pref > 0:
        req_score  = (len(matched_req)  / total_req)  * 70
        pref_score = (len(matched_pref) / total_pref) * 30
        score      = round(req_score + pref_score, 1)
    elif total_req > 0:
        score = round((len(matched_req) / total_req) * 100, 1)
    elif total_pref > 0:
        score = round((len(matched_pref) / total_pref) * 100, 1)
    else:
        score = 0.0

    print(f"  [OK] Matched required : {len(matched_req)}/{total_req}")
    print(f"  [OK] Matched preferred: {len(matched_pref)}/{total_pref}")
    print(f"  [OK] Critical gaps    : {len(critical)}")
    print(f"  [OK] Minor gaps       : {len(minor)}")
    print(f"  [OK] Match score      : {score}%")

    return {
        "score":             score,
        "matched_required":  matched_req,
        "matched_preferred": matched_pref,
        "critical_gaps":     critical,
        "minor_gaps":        minor,
        "total_required":    total_req,
        "total_preferred":   total_pref,
        "gaps":              {
            item["skill"]: item["recommendation"]
            for item in critical + minor
        },
    }