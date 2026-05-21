# app.py
from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
from reportlab.lib.units import cm # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_LEFT # type: ignore
import os
import json
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(__file__))

from modules.resume_parser import parse_resume
from modules.jd_analyzer   import analyze_jd
from modules.gap_analyzer  import analyze_gaps

app = Flask(__name__)

UPLOAD_FOLDER   = "uploads"
ALLOWED_EXT     = {"pdf"}
app.config["UPLOAD_FOLDER"]   = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("outputs",     exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@app.route("/")
def index():
    return render_template("index.html")

def generate_pdf_report(path, data, resume_name, ts):
    from reportlab.lib.pagesizes import A4 # type: ignore
    from reportlab.lib.styles import ParagraphStyle # type: ignore
    from reportlab.lib.units import cm # type: ignore
    from reportlab.lib import colors # type: ignore
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, # type: ignore
                                     Table, TableStyle, HRFlowable) # type: ignore
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT # type: ignore

    W, H   = A4
    INNER  = W - 4*cm   # usable width

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm
    )

    # ── Colors ────────────────────────────────────────────────────
    CA = colors.HexColor("#6244e5")   # accent
    CG = colors.HexColor("#1a7f37")   # green
    CR = colors.HexColor("#cf222e")   # red
    CY = colors.HexColor("#9a6700")   # amber
    CM = colors.HexColor("#656d76")   # muted
    CB = colors.HexColor("#f6f8fa")   # bg
    CD = colors.HexColor("#d0d7de")   # border
    CW = colors.white
    CK = colors.HexColor("#1f2328")   # black

    score       = data["score"]
    score_color = CG if score >= 70 else CY if score >= 40 else CR

    # ── Style factory ─────────────────────────────────────────────
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    TITLE   = S("T1", fontSize=20, fontName="Helvetica-Bold",
                textColor=CA, leading=26, spaceAfter=3)
    SUBT    = S("T2", fontSize=9,  fontName="Helvetica",
                textColor=CM, leading=13, spaceAfter=2)
    META    = S("T3", fontSize=8,  fontName="Helvetica",
                textColor=CM, leading=12, spaceAfter=14)
    SEC     = S("SE", fontSize=12, fontName="Helvetica-Bold",
                textColor=CK, leading=16, spaceBefore=16, spaceAfter=6)
    BODY    = S("BO", fontSize=10, fontName="Helvetica",
                textColor=CK, leading=15, spaceAfter=3)
    MUTED   = S("MU", fontSize=9,  fontName="Helvetica",
                textColor=CM, leading=13, spaceAfter=2)
    SCORE_S = S("SC", fontSize=48, fontName="Helvetica-Bold",
                textColor=score_color, leading=54)
    VERDICT = S("VE", fontSize=10, fontName="Helvetica",
                textColor=CM, leading=15, spaceAfter=4)
    FOOT    = S("FO", fontSize=8,  fontName="Helvetica",
                textColor=CM, leading=11, alignment=TA_CENTER)
    CHIP_S  = S("CH", fontSize=9,  fontName="Helvetica",
                textColor=CK, leading=12)
    CHIP_G  = S("CG", fontSize=9,  fontName="Helvetica",
                textColor=CG, leading=12)
    GAP_N   = S("GN", fontSize=10, fontName="Helvetica-Bold",
                textColor=CK, leading=14, spaceAfter=2)
    GAP_R   = S("GR", fontSize=9,  fontName="Helvetica",
                textColor=CM, leading=13, spaceAfter=0)

    elems = []

    # ── Header ────────────────────────────────────────────────────
    elems.append(Paragraph("AI Resume Skill Gap Analyzer", TITLE))
    elems.append(Paragraph(
        "Department of Centre For Artificial Intelligence — "
        "Madhav Institute of Technology &amp; Science (MITS), Gwalior", SUBT))
    formatted_ts = ts.replace("_", " ") if ts else ""
    elems.append(Paragraph(
        f"Generated: {formatted_ts}   |   Resume: {resume_name}", META))
    elems.append(HRFlowable(width="100%", thickness=0.5,
                             color=CD, spaceAfter=14))

    # ── Score block ───────────────────────────────────────────────
    verdict_map = [
        (80, "Strong match — you meet most requirements for this role."),
        (60, "Good match — a few key skills to strengthen before applying."),
        (40, "Partial match — work on the critical gaps first."),
        (0,  "Low match — significant upskilling needed for this role."),
    ]
    verdict_text = next(v for t, v in verdict_map if score >= t)

    score_inner = Table([
        [Paragraph(f"{score}%", SCORE_S)],
        [Paragraph("MATCH SCORE", S("SL", fontSize=8, fontName="Helvetica-Bold",
                                     textColor=CM, leading=11))],
        [Paragraph(verdict_text, VERDICT)],
        [Paragraph(
            f"Required matched: <b>{len(data['matched_required'])}/{data['total_required']}</b>    "
            f"Preferred matched: <b>{len(data['matched_preferred'])}/{data['total_preferred']}</b>    "
            f"Critical gaps: <b>{len(data['critical_gaps'])}</b>", BODY)],
    ], colWidths=[INNER - 2*cm])
    score_inner.setStyle(TableStyle([
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
    ]))

    score_wrap = Table([[score_inner]], colWidths=[INNER])
    score_wrap.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), CB),
        ("BOX",           (0,0),(-1,-1), 0.5, CD),
        ("LEFTPADDING",   (0,0),(-1,-1), 16),
        ("RIGHTPADDING",  (0,0),(-1,-1), 16),
        ("TOPPADDING",    (0,0),(-1,-1), 14),
        ("BOTTOMPADDING", (0,0),(-1,-1), 14),
    ]))
    elems.append(score_wrap)
    elems.append(Spacer(1, 14))

    # ── Skill chip rows ───────────────────────────────────────────
    def chip_rows(skills, style, bg, border_col):
        """Render skills as wrapped chip rows."""
        if not skills:
            return [Paragraph("None found.", MUTED)]

        CHIPS_PER_ROW = 5
        COL_W         = INNER / CHIPS_PER_ROW

        blocks  = []
        row_buf = []

        for i, s in enumerate(skills):
            cell = Table(
                [[Paragraph(s, style)]],
                colWidths=[COL_W - 8]
            )
            cell.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), bg),
                ("BOX",           (0,0),(-1,-1), 0.5, border_col),
                ("LEFTPADDING",   (0,0),(-1,-1), 7),
                ("RIGHTPADDING",  (0,0),(-1,-1), 7),
                ("TOPPADDING",    (0,0),(-1,-1), 3),
                ("BOTTOMPADDING", (0,0),(-1,-1), 3),
            ]))
            row_buf.append(cell)

            if len(row_buf) == CHIPS_PER_ROW or i == len(skills) - 1:
                # Pad row to full width
                while len(row_buf) < CHIPS_PER_ROW:
                    row_buf.append("")
                row_tbl = Table([row_buf], colWidths=[COL_W] * CHIPS_PER_ROW)
                row_tbl.setStyle(TableStyle([
                    ("LEFTPADDING",   (0,0),(-1,-1), 3),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 3),
                    ("TOPPADDING",    (0,0),(-1,-1), 3),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 3),
                    ("VALIGN",        (0,0),(-1,-1), "TOP"),
                ]))
                blocks.append(row_tbl)
                row_buf = []

        return blocks

    # ── Gap rows ──────────────────────────────────────────────────
    def gap_rows(items, left_color):
        if not items:
            return [Paragraph("None — great result!", MUTED)]

        blocks = []
        for g in items:
            skill = g["skill"] if isinstance(g, dict) else str(g)
            rec   = (g.get("recommendation", "") if isinstance(g, dict) else "")
            rec   = rec or "Search for relevant courses on Coursera or LinkedIn Learning."

            # Two-row inner table: skill name + recommendation
            inner = Table([
                [Paragraph(f"✕  {skill}" if left_color == CR
                           else f"◎  {skill}", GAP_N)],
                [Paragraph(f"→  {rec}", GAP_R)],
            ], colWidths=[INNER - 1.2*cm])
            inner.setStyle(TableStyle([
                ("LEFTPADDING",   (0,0),(-1,-1), 0),
                ("RIGHTPADDING",  (0,0),(-1,-1), 0),
                ("TOPPADDING",    (0,0),(-1,-1), 1),
                ("BOTTOMPADDING", (0,0),(-1,-1), 1),
            ]))

            outer = Table([[inner]], colWidths=[INNER])
            outer.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), CB),
                ("LINEBEFORE",    (0,0),(0,-1),  3, left_color),
                ("BOX",           (0,0),(-1,-1), 0.3, CD),
                ("LEFTPADDING",   (0,0),(-1,-1), 12),
                ("RIGHTPADDING",  (0,0),(-1,-1), 12),
                ("TOPPADDING",    (0,0),(-1,-1), 8),
                ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ]))
            blocks.append(outer)
            blocks.append(Spacer(1, 5))

        return blocks

    # ── Resume skills ─────────────────────────────────────────────
    elems.append(Paragraph(
        f"Your Skills  ({len(data['resume_skills'])})", SEC))
    elems.append(HRFlowable(width="100%", thickness=0.3,
                             color=CD, spaceAfter=6))
    elems.extend(chip_rows(data["resume_skills"], CHIP_S,
                            colors.HexColor("#f6f8fa"),
                            colors.HexColor("#d0d7de")))

    # ── Matched required ──────────────────────────────────────────
    matched_names = [
        (m["skill"] if isinstance(m, dict) else str(m))
        for m in data["matched_required"]
    ]
    elems.append(Paragraph(
        f"Matched Required  ({len(matched_names)}/{data['total_required']})", SEC))
    elems.append(HRFlowable(width="100%", thickness=0.3,
                             color=CD, spaceAfter=6))
    elems.extend(chip_rows(matched_names, CHIP_G,
                            colors.HexColor("#dafbe1"),
                            colors.HexColor("#74c68a")))

    # ── Critical gaps ─────────────────────────────────────────────
    elems.append(Paragraph(
        f"Critical Gaps  ({len(data['critical_gaps'])})", SEC))
    elems.append(HRFlowable(width="100%", thickness=0.3,
                             color=CD, spaceAfter=6))
    elems.extend(gap_rows(data["critical_gaps"], CR))

    # ── Minor gaps ────────────────────────────────────────────────
    elems.append(Paragraph(
        f"Minor Gaps  ({len(data['minor_gaps'])})", SEC))
    elems.append(HRFlowable(width="100%", thickness=0.3,
                             color=CD, spaceAfter=6))
    elems.extend(gap_rows(data["minor_gaps"], CY))

    # ── Footer ────────────────────────────────────────────────────
    elems.append(Spacer(1, 18))
    elems.append(HRFlowable(width="100%", thickness=0.5,
                             color=CD, spaceAfter=8))
    elems.append(Paragraph(
        "© 2025 Madhav Institute of Technology &amp; Science — "
        "Developed by Saksham Tundele, Prince Malviya & Tushar Malviya       |  AI Resume Skill Gap Analyzer",
        FOOT))

    doc.build(elems)

@app.route("/analyze", methods=["POST"])
def analyze():
    # ── Validate inputs ──────────────────────────────────────────
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file   = request.files["resume"]
    jd_text = request.form.get("jd_text", "").strip()

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported."}), 400
    if not jd_text:
        return jsonify({"error": "Job description cannot be empty."}), 400

    # ── Save uploaded file ────────────────────────────────────────
    filename  = secure_filename(file.filename)
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{ts}_{filename}")
    file.save(save_path)

    try:
        # ── Run pipeline ─────────────────────────────────────────
        resume_result = parse_resume(save_path)
        if not resume_result:
            return jsonify({"error": "Could not extract text from PDF."}), 400

        jd_result = analyze_jd(jd_text)
        if not jd_result:
            return jsonify({"error": "Could not analyze job description."}), 400

        gap_result = analyze_gaps(
            resume_result["skills"],
            jd_result["required_skills"],
            jd_result["preferred_skills"]
        )

        # ── Serialize for JSON ────────────────────────────────────
        def clean_list(lst):
            out = []
            for item in lst:
                if isinstance(item, dict):
                    out.append({
                        "skill": item.get("skill", str(item)),
                        "exact": item.get("exact", False),
                        "recommendation": item.get("recommendation", "")
                    })
                else:
                    out.append({"skill": str(item), "exact": False, "recommendation": ""})
            return out

        response = {
            "score":             round(gap_result["score"], 1),
            "resume_skills":     resume_result["skills"],
            "matched_required":  clean_list(gap_result["matched_required"]),
            "matched_preferred": clean_list(gap_result["matched_preferred"]),
            "critical_gaps":     clean_list(gap_result["critical_gaps"]),
            "minor_gaps":        clean_list(gap_result["minor_gaps"]),
            "total_required":    gap_result["total_required"],
            "total_preferred":   gap_result["total_preferred"],
        }

        # Save JSON (internal use)
        report_path = os.path.join("outputs", f"report_{ts}.json")
        with open(report_path, "w") as f:
            json.dump(response, f, indent=2)

        # Save PDF report
        pdf_path = os.path.join("outputs", f"report_{ts}.pdf")
        generate_pdf_report(pdf_path, response, file.filename, ts)

        response["report_id"] = ts
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up uploaded file
        if os.path.exists(save_path):
            os.remove(save_path)
            
@app.route("/download/<report_id>")
def download(report_id):
    path = os.path.join("outputs", f"report_{report_id}.pdf")
    if not os.path.exists(path):
        return "Report not found.", 404
    return send_file(path, as_attachment=True,
                     download_name=f"SkillGap_Report_{report_id}.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True, port=5000)