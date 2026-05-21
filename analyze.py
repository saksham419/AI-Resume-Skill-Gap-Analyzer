# analyze.py  — main CLI entry point
# Usage: python analyze.py --resume samples/sample_resume.pdf --jd samples/sample_jd.txt

import argparse
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

sys.path.insert(0, os.path.dirname(__file__))
from modules.resume_parser import parse_resume
from modules.jd_analyzer   import analyze_jd
from modules.gap_analyzer  import analyze_gaps

# ─── HELPERS ──────────────────────────────────────────────────────

def header(text):
    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 55)
    print(Fore.CYAN + Style.BRIGHT + f"  {text}")
    print(Fore.CYAN + Style.BRIGHT + "=" * 55)

def section(text):
    print(Fore.YELLOW + f"\n  {text}")
    print(Fore.YELLOW + "  " + "-" * 45)

def ok(text):    print(Fore.GREEN  + f"  ✔  {text}")
def gap(text):   print(Fore.RED    + f"  ✘  {text}")
def minor(text): print(Fore.YELLOW + f"  ◎  {text}")
def info(text):  print(Fore.WHITE  + f"     {text}")
def dim(text):   print(Style.DIM   + f"     {text}")

# ─── SCORE BAR ────────────────────────────────────────────────────

def score_bar(score):
    filled = int(score / 5)
    empty  = 20 - filled
    bar    = "█" * filled + "░" * empty
    if score >= 70:
        color = Fore.GREEN
    elif score >= 40:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    print(f"\n  {color}{Style.BRIGHT}Match Score:  {score:.1f}%")
    print(f"  {color}  [{bar}]")

# ─── REPORT BUILDER ───────────────────────────────────────────────

def build_report_text(resume_path, jd_path, resume_result, jd_result, gap_result):
    """Build a plain-text version of the report for saving."""
    lines = []
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("=" * 55)
    lines.append("  AI RESUME SKILL GAP ANALYZER — REPORT")
    lines.append("=" * 55)
    lines.append(f"  Generated : {ts}")
    lines.append(f"  Resume    : {resume_path}")
    lines.append(f"  Job desc  : {jd_path}")
    lines.append(f"  Score     : {gap_result['match_score']:.1f}%")
    lines.append("")

    lines.append("  RESUME SKILLS")
    lines.append("  " + "-" * 45)
    for s in resume_result["skills"]:
        lines.append(f"    • {s}")

    lines.append("")
    lines.append("  MATCHED REQUIRED SKILLS")
    lines.append("  " + "-" * 45)
    for s, how in gap_result["matched_required"]:
        lines.append(f"    ✔  {s:<28} ({how})")

    lines.append("")
    lines.append("  CRITICAL GAPS")
    lines.append("  " + "-" * 45)
    for s in gap_result["critical_gaps"]:
        rec = gap_result["recommendations"].get(s, "")
        lines.append(f"    ✘  {s}")
        if rec:
            lines.append(f"       → {rec}")

    lines.append("")
    lines.append("  MINOR GAPS (preferred skills)")
    lines.append("  " + "-" * 45)
    for s in gap_result["minor_gaps"]:
        rec = gap_result["recommendations"].get(s, "")
        lines.append(f"    ◎  {s}")
        if rec:
            lines.append(f"       → {rec}")

    lines.append("")
    lines.append("=" * 55)
    return "\n".join(lines)


def save_report(text, output_dir="outputs"):
    """Save report to outputs/ folder with timestamp."""
    os.makedirs(output_dir, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"report_{ts}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename


# ─── PRINT RESULTS ────────────────────────────────────────────────
def print_results(resume_result, jd_result, gap_result):

    header("AI RESUME SKILL GAP ANALYZER")
    score_bar(gap_result["score"])

    # Resume skills
    section(f"YOUR SKILLS  ({len(resume_result['skills'])} found)")
    for s in resume_result["skills"]:
        ok(s)

    # Matched required
    matched = gap_result["matched_required"]
    section(f"MATCHED REQUIRED  ({len(matched)}/{gap_result['total_required']})")
    for item in matched:
        skill  = item["skill"]
        how    = "exact" if item.get("exact") else "similar"
        ok(f"{skill:<28}  ({how})")

    # Matched preferred
    matched_pref = gap_result["matched_preferred"]
    section(f"MATCHED PREFERRED  ({len(matched_pref)}/{gap_result['total_preferred']})")
    if matched_pref:
        for item in matched_pref:
            skill = item["skill"]
            how   = "exact" if item.get("exact") else "similar"
            ok(f"{skill:<28}  ({how})")
    else:
        dim("None matched")

    # Critical gaps
    critical = gap_result["critical_gaps"]
    section(f"CRITICAL GAPS  ({len(critical)})  — must learn for this role")
    for item in critical:
        skill = item["skill"] if isinstance(item, dict) else item
        rec   = item.get("recommendation", "") if isinstance(item, dict) else ""
        gap(skill)
        if rec:
            dim(f"→ {rec}")

    # Minor gaps
    minor_gaps = gap_result["minor_gaps"]
    section(f"MINOR GAPS  ({len(minor_gaps)})  — preferred / good to have")
    for item in minor_gaps:
        skill = item["skill"] if isinstance(item, dict) else item
        rec   = item.get("recommendation", "") if isinstance(item, dict) else ""
        minor(skill)
        if rec:
            dim(f"→ {rec}")

    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 55 + "\n")


def build_report_text(resume_path, jd_path, resume_result, jd_result, gap_result):
    lines = []
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("=" * 55)
    lines.append("  AI RESUME SKILL GAP ANALYZER — REPORT")
    lines.append("=" * 55)
    lines.append(f"  Generated : {ts}")
    lines.append(f"  Resume    : {resume_path}")
    lines.append(f"  Job desc  : {jd_path}")
    lines.append(f"  Score     : {gap_result['score']:.1f}%")
    lines.append("")

    lines.append("  RESUME SKILLS")
    lines.append("  " + "-" * 45)
    for s in resume_result["skills"]:
        lines.append(f"    • {s}")

    lines.append("")
    lines.append("  MATCHED REQUIRED SKILLS")
    lines.append("  " + "-" * 45)
    for item in gap_result["matched_required"]:
        skill = item["skill"]
        how   = "exact" if item.get("exact") else "similar"
        lines.append(f"    ✔  {skill:<28} ({how})")

    lines.append("")
    lines.append("  CRITICAL GAPS")
    lines.append("  " + "-" * 45)
    for item in gap_result["critical_gaps"]:
        skill = item["skill"] if isinstance(item, dict) else item
        rec   = item.get("recommendation", "") if isinstance(item, dict) else ""
        lines.append(f"    ✘  {skill}")
        if rec:
            lines.append(f"       → {rec}")

    lines.append("")
    lines.append("  MINOR GAPS (preferred skills)")
    lines.append("  " + "-" * 45)
    for item in gap_result["minor_gaps"]:
        skill = item["skill"] if isinstance(item, dict) else item
        rec   = item.get("recommendation", "") if isinstance(item, dict) else ""
        lines.append(f"    ◎  {skill}")
        if rec:
            lines.append(f"       → {rec}")

    lines.append("")
    lines.append("=" * 55)
    return "\n".join(lines)
# ─── MAIN ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Skill Gap Analyzer",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--resume", required=True,
                        help="Path to resume PDF\n  e.g. samples/sample_resume.pdf")
    parser.add_argument("--jd",     required=True,
                        help="Path to job description .txt file\n  e.g. samples/sample_jd.txt")
    parser.add_argument("--save",   action="store_true",
                        help="Save report to outputs/ folder")
    args = parser.parse_args()

    # Validate inputs
    if not os.path.exists(args.resume):
        print(Fore.RED + f"[ERROR] Resume not found: {args.resume}")
        sys.exit(1)
    if not os.path.exists(args.jd):
        print(Fore.RED + f"[ERROR] JD file not found: {args.jd}")
        sys.exit(1)

    # Run pipeline
    with open(args.jd, "r", encoding="utf-8") as f:
        jd_text = f.read()

    resume_result = parse_resume(args.resume)
    jd_result     = analyze_jd(jd_text)

    if not resume_result or not jd_result:
        print(Fore.RED + "[ERROR] Could not process inputs.")
        sys.exit(1)

    gap_result = analyze_gaps(
        resume_result["skills"],
        jd_result["required_skills"],
        jd_result["preferred_skills"]
    )

    # Print colored report
    print_results(resume_result, jd_result, gap_result)

    # Save if requested
    if args.save:
        report_text = build_report_text(
            args.resume, args.jd,
            resume_result, jd_result, gap_result
        )
        path = save_report(report_text)
        print(Fore.GREEN + f"  Report saved → {path}\n")


if __name__ == "__main__":
    main()