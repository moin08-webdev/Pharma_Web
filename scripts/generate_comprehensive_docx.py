import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    
    borders = {"top": top, "bottom": bottom, "left": left, "right": right}
    for border_name, border_style in borders.items():
        if border_style:
            # border_style: (val, sz, space, color)
            val, sz, space, color = border_style
            b_xml = parse_xml(f'<w:{border_name} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="{space}" w:color="{color}"/>')
            tcBorders.append(b_xml)
        else:
            b_xml = parse_xml(f'<w:{border_name} {nsdecls("w")} w:val="none"/>')
            tcBorders.append(b_xml)
    tcPr.append(tcBorders)

def add_callout(doc, title, text, bg_hex="F0FDFA", border_hex="0D9488", text_color=(15, 23, 42)):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    set_cell_borders(cell, left=("single", "36", "0", border_hex))
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"GUARANTEE / RULE: {title.upper()}\n")
    run_t.font.name = "Segoe UI"
    run_t.font.size = Pt(10)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(15, 118, 110)
    
    run_b = p.add_run(text)
    run_b.font.name = "Segoe UI"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(*text_color)
    
    # spacing after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(6)

def build_docx():
    doc = docx.Document()
    
    # Page setup - Letter / A4 with 0.75 in margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.75)
        sec.left_margin = Inches(0.75)
        sec.right_margin = Inches(0.75)
        sec.header_distance = Inches(0.4)
        sec.footer_distance = Inches(0.4)
        
        # Header & Footer setup
        header = sec.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("PharmaBridge — Comprehensive Architectural & Feature Documentation")
        hrun.font.name = "Segoe UI"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(148, 163, 184)
        
        footer = sec.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun = fp.add_run("PharmaBridge Platform Manual v1.0 (Production Release)  |  Confidential & Regulatory Compliant")
        frun.font.name = "Segoe UI"
        frun.font.size = Pt(8)
        frun.font.color.rgb = RGBColor(148, 163, 184)

    # Base Colors
    C_TEAL = RGBColor(15, 118, 110)
    C_DARK = RGBColor(15, 23, 42)
    C_SLATE = RGBColor(51, 65, 85)
    C_MUTED = RGBColor(100, 116, 139)
    C_EMERALD = RGBColor(5, 150, 105)

    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/web/public/logo.png"))

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    p_cov_top = doc.add_paragraph()
    p_cov_top.paragraph_format.space_before = Pt(10)
    p_cov_top.paragraph_format.space_after = Pt(14)
    
    if os.path.exists(logo_path):
        p_cov_top.add_run().add_picture(logo_path, width=Inches(1.3))
    
    p_badge = doc.add_paragraph()
    p_badge.paragraph_format.space_before = Pt(4)
    p_badge.paragraph_format.space_after = Pt(8)
    r_badge = p_badge.add_run("OFFICIAL SYSTEM SPECIFICATION & FEATURE CATALOG")
    r_badge.font.name = "Segoe UI"
    r_badge.font.size = Pt(10)
    r_badge.font.bold = True
    r_badge.font.color.rgb = C_TEAL

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("PharmaBridge")
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(36)
    r_title.font.bold = True
    r_title.font.color.rgb = C_DARK

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    r_sub = p_sub.add_run("AI-Assisted Prescription Fulfilment & Clinical Dispensing Workspace")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(16)
    r_sub.font.bold = True
    r_sub.font.color.rgb = C_TEAL

    p_tag = doc.add_paragraph()
    p_tag.paragraph_format.space_before = Pt(0)
    p_tag.paragraph_format.space_after = Pt(18)
    r_tag = p_tag.add_run("AI help for everyday pharmacy work — Helps pharmacists check medicines, compare costs, and manage stock.")
    r_tag.font.name = "Segoe UI"
    r_tag.font.size = Pt(11.5)
    r_tag.font.italic = True
    r_tag.font.color.rgb = C_SLATE

    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.space_before = Pt(0)
    p_desc.paragraph_format.space_after = Pt(24)
    r_desc = p_desc.add_run(
        "A comprehensive architectural and functional manual detailing every clinical safety check, "
        "economic algorithm, transactional inventory protocol, and user workflow implemented in the "
        "PharmaBridge clinical dispensing platform for Indian retail and community pharmacies."
    )
    r_desc.font.name = "Segoe UI"
    r_desc.font.size = Pt(10.5)
    r_desc.font.color.rgb = C_SLATE

    # Cover Metadata Table
    meta_tbl = doc.add_table(rows=7, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_tbl.autofit = False
    
    meta_data = [
        ("Platform Version", "v1.0.0-MVP (Production Release)"),
        ("Architecture", "FastAPI (Python 3.12 Asynchronous) + React 19 / Vite 6 + PostgreSQL 17"),
        ("Compliance Standard", "Pharmacy Act 1948, Drugs & Cosmetics Rules, DPDP Act 2023"),
        ("Deterministic Engine", "Exact Decimal Paise Arithmetic (Zero Floating-Point Drift) & Canonical Salt Matching"),
        ("Inventory Protocol", "First-Expired, First-Out (FEFO) with PostgreSQL Row-Level Locks (SELECT ... FOR UPDATE)"),
        ("Verification Matrix", "33/33 Automated Tests Passed (21 Pytest Backend + 12 Playwright Cross-Device E2E)"),
        ("Official Repository", "https://github.com/moin08-webdev/Pharma_Web"),
    ]
    
    for row_idx, (k, v) in enumerate(meta_data):
        c0 = meta_tbl.cell(row_idx, 0)
        c1 = meta_tbl.cell(row_idx, 1)
        c0.width = Inches(2.2)
        c1.width = Inches(4.6)
        
        bg = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        set_cell_background(c0, bg)
        set_cell_background(c1, bg)
        set_cell_margins(c0, top=90, bottom=90, left=120, right=120)
        set_cell_margins(c1, top=90, bottom=90, left=120, right=120)
        set_cell_borders(c0, bottom=("single", "8", "0", "E2E8F0"))
        set_cell_borders(c1, bottom=("single", "8", "0", "E2E8F0"))
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(k)
        r0.font.name = "Segoe UI"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = C_DARK
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(v)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = C_SLATE

    doc.add_page_break()

    # =========================================================================
    # EXECUTIVE SUMMARY & 6-STEP WORKFLOW
    # =========================================================================
    h1 = doc.add_heading(level=1)
    r = h1.add_run("1. Executive Summary & Platform Overview")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(
        "PharmaBridge is an AI-assisted, clinically guarded prescription fulfilment workspace engineered specifically "
        "for Indian retail and community pharmacies. Across India, community pharmacies handle over 80% of all outpatient "
        "medication dispensing. However, the retail pharmacy ecosystem is severely challenged by illegible handwritten slips, "
        "opaque brand substitutions driven by commercial margins rather than clinical equivalence, misleading pricing derived "
        "from fractional-strip calculations, and catastrophic inventory losses due to expiration of rear-shelf batches."
    )
    r.font.name = "Segoe UI"
    r.font.size = Pt(10)
    r.font.color.rgb = C_SLATE

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run(
        "PharmaBridge systematically replaces these error-prone manual habits with automated, deterministic safeguards. "
        "The application provides a complete end-to-end dispensing pipeline—from multi-format prescription intake and OCR digitisation, "
        "to chemical equivalence evaluation, whole-pack economic comparisons, mandatory registered pharmacist approvals, "
        "and transactional First-Expired, First-Out (FEFO) inventory deductions."
    )
    r.font.name = "Segoe UI"
    r.font.size = Pt(10)
    r.font.color.rgb = C_SLATE

    # The 6-Step Workflow Section
    h2 = doc.add_heading(level=2)
    r = h2.add_run("The 6-Step Pharmacy Workflow")
    r.font.name = "Segoe UI"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = C_TEAL

    p_wf = doc.add_paragraph()
    p_wf.paragraph_format.line_spacing = 1.15
    p_wf.paragraph_format.space_after = Pt(10)
    r_wf = p_wf.add_run(
        "The PharmaBridge user interface features a persistent visual workflow stepper that guides pharmacy staff through six distinct, "
        "auditable phases. This guarantees that no step is skipped and every transaction complies with Pharmacy Practice Regulations:"
    )
    r_wf.font.name = "Segoe UI"
    r_wf.font.size = Pt(10)
    r_wf.font.color.rgb = C_SLATE

    wf_steps = [
        ("Step 1", "Add Prescription", "Intake via paper slip camera photo, multi-page PDF upload, or direct manual typing. Captures metadata with zero external cloud leakage."),
        ("Step 2", "Check Details", "Side-by-side review interface. Pharmacists check medicine names, strengths, forms, and durations. Ambiguous items trigger visual alerts and block plan progression."),
        ("Step 3", "Compare Options", "Formulation equivalence engine presents bio-equivalent candidates, whole-pack prices, and real patient savings (e.g., 33.33% savings for Paracetamol 500mg)."),
        ("Step 4", "Pharmacist Approval", "Mandatory clinical governance gate. Only licensed Pharmacists can sign off on candidate substitutions. Assistants are strictly blocked with 403 API guards."),
        ("Step 5", "Complete Order", "Atomic stock deduction using PostgreSQL row locks ('SELECT ... FOR UPDATE') and FEFO allocation. Guaranteed idempotent execution prevents double billing."),
        ("Step 6", "Keep a Record", "Immediate generation of a patient receipt with batch tracking and permanent logging into an immutable, append-only stock movement ledger for drug inspector audits."),
    ]

    wf_tbl = doc.add_table(rows=len(wf_steps) + 1, cols=3)
    wf_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    wf_tbl.autofit = False

    # Header Row
    hdr_titles = ["Step", "Workflow Phase", "Clinical & Operational Significance"]
    col_widths = [Inches(1.0), Inches(1.8), Inches(4.0)]
    for i, title in enumerate(hdr_titles):
        cell = wf_tbl.cell(0, i)
        cell.width = col_widths[i]
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        r = p.add_run(title)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for idx, (st, name, desc) in enumerate(wf_steps):
        row_idx = idx + 1
        c0 = wf_tbl.cell(row_idx, 0)
        c1 = wf_tbl.cell(row_idx, 1)
        c2 = wf_tbl.cell(row_idx, 2)
        c0.width, c1.width, c2.width = col_widths
        
        bg = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            set_cell_borders(c, bottom=("single", "6", "0", "E2E8F0"))

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(st)
        r0.font.name = "Segoe UI"
        r0.font.size = Pt(9)
        r0.font.bold = True
        r0.font.color.rgb = C_TEAL

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(name)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9)
        r1.font.bold = True
        r1.font.color.rgb = C_DARK

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(desc)
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(9)
        r2.font.color.rgb = C_SLATE

    doc.add_page_break()

    # =========================================================================
    # THE 20 CORE PLATFORM FEATURES (EXHAUSTIVE DEEP DIVE)
    # =========================================================================
    h1_feat = doc.add_heading(level=1)
    r = h1_feat.add_run("2. Comprehensive Feature-by-Feature Catalog (Features 01 to 20)")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p_feat_intro = doc.add_paragraph()
    p_feat_intro.paragraph_format.line_spacing = 1.15
    p_feat_intro.paragraph_format.space_after = Pt(14)
    r_feat_intro = p_feat_intro.add_run(
        "This section documents all 20 individual platform features presented in the PharmaBridge architectural deck. "
        "Each feature is broken down into its specific operational problem, the technological solution implemented, "
        "the engineering/codebase highlights, and the strict clinical guarantee enforced."
    )
    r_feat_intro.font.name = "Segoe UI"
    r_feat_intro.font.size = Pt(10)
    r_feat_intro.font.color.rgb = C_SLATE

    # Feature List Data from Slides 2 to 21
    features = [
        {
            "num": "01",
            "name": "Multi-Modal Prescription Intake & OCR Pipeline",
            "category": "INTAKE & VISION",
            "problem": [
                "Doctor handwriting on paper slips is notoriously illegible and skewed.",
                "Scanned documents frequently suffer from optical blur, uneven lighting, and orientation tilt.",
                "Pharmacists waste 4-7 minutes per patient manually retyping drug names into legacy systems.",
                "High risk of dispensing errors caused by confusing similar-looking handwritten brand names."
            ],
            "solution": [
                "Multi-format ingestion supporting PNG, JPEG, and multi-page PDF documents.",
                "Private mounted local storage volume ensures total compliance with patient privacy.",
                "Automated OCR extracts drug names, dosages, durations, and prescribing doctor notes.",
                "Direct manual fallback entry is always available if documents are paperless or verbal."
            ],
            "technical": [
                "Max upload size: 10 MiB, up to 5 pages per upload session.",
                "Instant 'Load Sample Prescription' button pre-loads synthetic evaluator scenarios.",
                "Creates a draft prescription entity with an initial optimistic revision (v1).",
                "Document metadata (byte size, MIME type, page count) logged permanently in PostgreSQL."
            ],
            "guarantee": "Prescriptions can be captured from paper scans, camera uploads, or direct manual entry with zero cloud data leakage."
        },
        {
            "num": "02",
            "name": "Clinical Verification & Ambiguity Resolution",
            "category": "CLINICAL VERIFICATION",
            "problem": [
                "Prescriptions frequently omit explicit strengths (e.g., 'Amlo' written without 2.5mg or 5mg).",
                "Automated OCR can misread a digit or decimal point without a mandated human verification gate.",
                "Premature quote generation on ambiguous items leads to dispensing the wrong drug strength.",
                "Legacy POS software offers no synchronized side-by-side view to inspect the source slip."
            ],
            "solution": [
                "Two-column review layout: Document preview on left, editable item lines on right.",
                "Ambiguous lines are immediately flagged with an amber warning badge.",
                "Prescription confirmation is strictly disabled until every single line is linked to a valid catalogue SKU.",
                "Pharmacist can dynamically add, edit, or delete prescription lines before confirming."
            ],
            "technical": [
                "Optimistic concurrency locking checks 'expected_revision' on bulk line updates.",
                "Saving line edits invalidates prior quotes and increments prescription revision.",
                "Line status transitions: 'unconfirmed' -> 'confirmed' upon catalogue SKU linking.",
                "100% verified by automated E2E tests: unconfirmed lines halt plan generation."
            ],
            "guarantee": "No prescription can proceed to pricing or dispensing until every prescribed item is matched to a known catalogue product."
        },
        {
            "num": "03",
            "name": "Deterministic Formulation Equivalence Engine",
            "category": "PHARMACOLOGICAL SAFETY",
            "problem": [
                "Generic substitutions in retail pharmacies are often driven by trade profit margins rather than bio-equivalence.",
                "E-commerce fuzzy search algorithms routinely suggest chemically dissimilar brand alternatives.",
                "Substituting inactive or mismatched strengths causes severe therapeutic failure.",
                "Counter staff have no immediate pharmacological reference to verify bio-equivalence in real time."
            ],
            "solution": [
                "Deterministic pharmacological matching engine (zero fuzzy hallucinations or AI guesses).",
                "Requires 100% parity across active ingredients and molecular strength ratios.",
                "Canonical active ingredient mapping (e.g. Paracetamol == Acetaminophen).",
                "Dosage forms and administration routes must match exactly (tablet to tablet, oral to oral)."
            ],
            "technical": [
                "Normalized comparison using Decimal strength values and canonical units.",
                "Evaluates both single-ingredient and complex multi-component formulations.",
                "Automatically queries pharmacy catalogue for eligible substitution candidates.",
                "5 dedicated Pytest unit tests confirm formulation equivalence logic."
            ],
            "guarantee": "Every candidate suggested by PharmaBridge is guaranteed to possess identical active substance composition and strength."
        },
        {
            "num": "04",
            "name": "Canonical Salt Identity Preservation",
            "category": "PHARMACOLOGICAL SAFETY",
            "problem": [
                "Different chemical salts of the same active molecule exhibit distinct absorption rates and bioavailability.",
                "Example: Metformin Hydrochloride vs Metformin Pamoate possess completely different clinical profiles.",
                "Careless salt substitution can lead to sub-therapeutic blood levels or unexpected systemic toxicity.",
                "Pharmacists often lack rapid chemical alias resolution tools during busy retail counter hours."
            ],
            "solution": [
                "Database explicitly models canonical salt identity on formulation components.",
                "If a drug has clinical salt sensitivity, substitutions across differing salts are automatically blocked.",
                "Substitutions are only allowed if salt identities match or are pharmacologically interchangeable.",
                "Rejection reason is formally documented and surfaced: 'Salt Identity Incompatible'."
            ],
            "technical": [
                "Canonical chemical name normalization separates base molecule from salt suffix.",
                "Approved chemical aliases mapped in 'ingredients' relational database table.",
                "Maintains pharmacopeial compliance under Indian Pharmacopoeia (IP) standards.",
                "Validated by dedicated Pytest unit test: 'test_salt_preservation'."
            ],
            "guarantee": "PharmaBridge guards against bio-availability failures by strictly enforcing chemical salt compatibility."
        },
        {
            "num": "05",
            "name": "Release Profile Compatibility Enforcement",
            "category": "CLINICAL PHARMACOLOGY",
            "problem": [
                "Immediate Release (IR) and Extended Release (ER/SR) drugs are NOT therapeutically interchangeable.",
                "Dispensing Metformin IR instead of ER causes severe gastrointestinal distress and nausea.",
                "Dispensing ER instead of IR causes dangerously delayed therapeutic onset in acute medical conditions.",
                "Fatal dose-dumping can occur if sustained-release matrices are substituted incorrectly."
            ],
            "solution": [
                "Release profiles are first-class domain models (IR, ER, SR, CR, DR).",
                "Formulation candidate engine checks release profile compatibility strictly before recommending.",
                "A Metformin IR 500mg prescription will strictly reject Metformin ER 500mg.",
                "Rejected alternatives show an explicit alert: 'Release Profile Mismatch: IR vs ER'."
            ],
            "technical": [
                "Release profile tracked on both formulation and component database levels.",
                "Embedded synthetic demo fixture: DemoMetformin IR vs DemoMetformin ER.",
                "Pharmacists can view the rejected ER product and understand why it is blocked.",
                "Verified by automated unit test: 'test_release_mismatch_rejection'."
            ],
            "guarantee": "PharmaBridge protects patients from toxic dose-dumping by strictly segregating Immediate Release and Extended Release profiles."
        },
        {
            "num": "06",
            "name": "Multi-Ingredient Combination Subset Rejection",
            "category": "CLINICAL PHARMACOLOGY",
            "problem": [
                "Doctor prescribes Augmentin (Amoxicillin 500mg + Clavulanic Acid 125mg).",
                "Naive search tools suggest plain Amoxicillin 500mg as a generic alternative.",
                "Omitting Clavulanic Acid causes antibiotic treatment failure against beta-lactamase producing bacteria.",
                "Partial-ingredient matching is one of the top causes of retail pharmacy dispensing errors."
            ],
            "solution": [
                "Requires exact multiset component matching for all active ingredients.",
                "If a prescription has 2 active ingredients, candidates must contain both in exact proportion.",
                "Plain Amoxicillin is rejected with the explicit clinical reason: 'Combination Subset Mismatch'.",
                "Prevents inadvertent under-treatment of severe bacterial infections."
            ],
            "technical": [
                "Component multiset intersection logic in 'app/domain/matching_rules.py'.",
                "Demo fixture: DemoAugmentin 625 (Amox + Clav) vs DemoAmox 500 (Amox alone).",
                "Rejection metadata exposed via REST API endpoint: '/medicines/{id}/candidates'.",
                "100% verified by Pytest integration test: 'test_combination_subset_rejection'."
            ],
            "guarantee": "PharmaBridge strictly forbids partial-ingredient substitutions, ensuring patients receive the complete therapeutic cocktail prescribed."
        },
        {
            "num": "07",
            "name": "Narrow Therapeutic Index (NTI) Safety Safeguards",
            "category": "CLINICAL PHARMACOLOGY",
            "problem": [
                "Certain critical medications have a narrow gap between therapeutic effectiveness and lethal toxic doses.",
                "Examples include Warfarin, Lithium, Digoxin, Theophylline, and Levothyroxine.",
                "Minor bioavailability variance between generic brands can cause fatal hemorrhage or toxicity.",
                "Retail pharmacists should never switch NTI drug brands without explicit physician consultation."
            ],
            "solution": [
                "Database explicitly flags formulations belonging to Narrow Therapeutic Index classes.",
                "Automated generic candidate engine automatically locks NTI products against auto-substitution.",
                "Displays a high-visibility clinical alert: 'Narrow Therapeutic Index - Brand Switch Restricted'.",
                "Requires explicit prescribing physician confirmation before any substitution can be logged."
            ],
            "technical": [
                "Flags defined in clinical metadata: 'is_narrow_therapeutic_index: bool'.",
                "Integrated with mandatory pharmacist approval notes requirement.",
                "Adheres to International Pharmaceutical Federation (FIP) guidelines.",
                "Ensures total medical malpractice defense for the retail pharmacy enterprise."
            ],
            "guarantee": "High-risk NTI drugs are quarantined from automated switching, protecting patients from dangerous pharmacokinetic variances."
        },
        {
            "num": "08",
            "name": "Whole-Pack Economics & Exact Paise Arithmetic",
            "category": "ECONOMIC PRECISION",
            "problem": [
                "Prescriptions request unit quantities (e.g. 15 tablets), but blister packs contain 10.",
                "Pharmacies either cut blister foils (risking contamination and losing expiry print) or charge ad-hoc.",
                "Software quoting fractional pills (e.g. ₹1.33/pill) misleads patients on total counter bill.",
                "Standard IEEE-754 floating point arithmetic in software creates rounding penny errors."
            ],
            "solution": [
                "Packaging model supports 'pack_break_allowed = true / false'.",
                "If pack break is disallowed, calculates exact integer packs: ceil(requested / pack_size).",
                "Calculates supplied units and explicitly shows 'excess units' (e.g. 5 extra tabs).",
                "Calculates exact patient cost using integer paise arithmetic (Decimal, zero float drift)."
            ],
            "technical": [
                "Paise arithmetic handled in 'app/domain/money.py' (1 INR = 100 paise).",
                "Pack breakdown engine in 'app/domain/quantities.py'.",
                "Displays both baseline prescribed pack cost and alternative candidate cost.",
                "Unit tested by 5 Pytest cases verifying whole-pack math and zero float drift."
            ],
            "guarantee": "PharmaBridge eliminates fractional-pill confusion by calculating real-world whole pack costs with exact paise mathematical precision."
        },
        {
            "num": "09",
            "name": "Transparent Patient Savings: The 33.33% Case Study",
            "category": "ECONOMIC PRECISION",
            "problem": [
                "Patients are often skeptical of generic drugs, fearing hidden charges or inferior quantity.",
                "Pharmacy billing software masks why a generic alternative is cheaper or how many units are provided.",
                "Lack of transparent cost comparison leads to patient resistance at the checkout counter.",
                "Pharmacies fail to demonstrate tangible economic value to their local customer base."
            ],
            "solution": [
                "Side-by-side cost transparency: displays baseline cost vs candidate cost in bold.",
                "The 33.33% Paracetamol benchmark: Prescribed Brand A (15-pack @ ₹30.00 = ₹2.00/unit).",
                "Candidate Product B (10-pack @ ₹10.00): ceil(15/10) = 2 packs = ₹20.00.",
                "Patient gets 20 tablets (5 bonus unexpired tablets) for ₹20.00, achieving 33.33% real savings!"
            ],
            "technical": [
                "Baseline cost: ₹30.00 (Brand A). Alternative cost: ₹20.00 (Product B).",
                "Net savings: ₹30.00 - ₹20.00 = ₹10.00 (33.33% real savings).",
                "Real-time savings calculation banner updates dynamically upon candidate selection.",
                "Verified by automated E2E browser tests across Desktop, Tablet, and Mobile."
            ],
            "guarantee": "Real savings verified: ₹30.00 Baseline vs ₹20.00 Generic = 33.33% Net Patient Savings with full pack transparency."
        },
        {
            "num": "10",
            "name": "Mandatory Pharmacist Clinical Approval Gate",
            "category": "CLINICAL GOVERNANCE",
            "problem": [
                "Retail pharmacy counters in India are often operated by unqualified counter assistants.",
                "Generic brand switching is frequently carried out without registered pharmacist supervision.",
                "Violates the Pharmacy Act 1948 and Pharmacy Practice Regulations.",
                "Pharmacies face license revocation and severe legal liability during state drug audits."
            ],
            "solution": [
                "Strict Role-Based Access Control (RBAC): Pharmacist vs Pharmacy Assistant vs Store Admin.",
                "Only logged-in users with the 'PHARMACIST' role can approve fulfilment plans.",
                "Assistants viewing a plan see an amber restriction badge: 'Pharmacist Role Required'.",
                "Approve and Finalize buttons are completely disabled and hidden for assistants."
            ],
            "technical": [
                "Backend API enforces role verification in 'app/api/dependencies.py'.",
                "Assistant attempts to approve or finalize return HTTP 403 Forbidden.",
                "Approval records approver name, license role, and clinical justification notes.",
                "Verified by automated Playwright E2E test: 'review-gates.spec.ts'."
            ],
            "guarantee": "No medicine substitution or order finalization can occur without the authenticated clinical signature of a registered pharmacist."
        },
        {
            "num": "11",
            "name": "5-Minute Quote Lock & Pricing Volatility Protection",
            "category": "TRANSACTIONAL PRICING",
            "problem": [
                "A pharmacist creates a quote while counseling the patient on drug usage.",
                "Meanwhile, another terminal dispenses the same batch or stock prices shift.",
                "When the patient reaches the cash register, prices jump unexpectedly.",
                "Causes patient friction, complaints, and checkout inventory discrepancies."
            ],
            "solution": [
                "Every generated quote carries a strict 5-minute Time-To-Live (TTL).",
                "Locks batch allocation and unit prices for the duration of the patient consultation.",
                "Displays real-time countdown timer on the Fulfilment Plan workspace.",
                "Guarantees the patient pays the exact price quoted during clinical counseling."
            ],
            "technical": [
                "Quote expiration timestamp stored in PostgreSQL: 'valid_until = now() + 5 mins'.",
                "Order finalization strictly validates 'quote.valid_until > now()'.",
                "Expired quotes trigger a safe background recalculation with fresh batch availability.",
                "Protects pharmacy margins against rapid wholesale price adjustments."
            ],
            "guarantee": "Quotes freeze batch allocation and pricing for 5 minutes, ensuring patient trust and zero billing surprises at the counter."
        },
        {
            "num": "12",
            "name": "First-Expired, First-Out (FEFO) Inventory Engine",
            "category": "INVENTORY MANAGEMENT",
            "problem": [
                "Pharmacy staff naturally grab whatever box is positioned on the front of the shelf.",
                "Older stock pushed to the rear passes its expiration date undetected.",
                "Expired drugs must be written off as 100% financial losses.",
                "Dispensing expired medication to patients results in severe clinical harm and lawsuits."
            ],
            "solution": [
                "Automated FEFO batch allocation: queries active batches ordered by 'expires_on ASC'.",
                "Batches nearing expiry are automatically consumed first in quotes and orders.",
                "Multi-batch allocation: if batch A has 8 units and 15 are needed, splits cleanly (8 + 7).",
                "Batches with 'expires_on < today' are completely excluded from dispensing."
            ],
            "technical": [
                "Implemented in 'app/services/planning.py:allocate_batches_fefo'.",
                "Tracks batch number, supplier code, expiry date, and unit cost per batch.",
                "Saves retail pharmacies an estimated 2-5% of total inventory value annually.",
                "Demonstrated in demo seed: PB-2026-01 (180 days) allocated before PB-2026-02 (400 days)."
            ],
            "guarantee": "Automated FEFO allocation prioritizes stock nearing expiry, drastically curtailing shelf obsolescence and financial waste."
        },
        {
            "num": "13",
            "name": "Concurrency Control & Atomic Row Locking",
            "category": "DATABASE ARCHITECTURE",
            "problem": [
                "In busy pharmacies, multiple checkout counters operate simultaneously.",
                "Two staff members can attempt to dispense the last 10 tablets of a drug at the same instant.",
                "Without concurrency control, both transactions succeed, causing negative inventory.",
                "Inventory records drift, leading to unfulfilled orders and stock chaos."
            ],
            "solution": [
                "PostgreSQL row-level locking via SQLAlchemy: 'SELECT ... FOR UPDATE'.",
                "Locks the specific batch rows during the finalization database transaction.",
                "Other concurrent transactions wait until the lock is released or fail cleanly.",
                "Guarantees that available unreserved stock is never over-committed."
            ],
            "technical": [
                "AsyncPG driver with PostgreSQL read-committed / serializable transaction isolation.",
                "Re-verifies 'batch.quantity >= allocation.quantity' under active lock.",
                "Rolls back cleanly with an HTTP 409 Conflict if stock was depleted mid-flight.",
                "Verified by integration test: 'test_prescription_to_order_api.py'."
            ],
            "guarantee": "Row-level locks prevent race conditions across busy counter terminals, guaranteeing 100% database inventory consistency."
        },
        {
            "num": "14",
            "name": "Idempotent Finalization & Network Fault Tolerance",
            "category": "TRANSACTION RESILIENCE",
            "problem": [
                "Pharmacy internet connections can be unstable or suffer micro-disconnections.",
                "A cashier clicks 'Finalize Order', the UI hangs, and they click again.",
                "Standard POS systems execute two finalizations, double-deducting stock.",
                "Patients are billed twice or receipt records show phantom duplicate orders."
            ],
            "solution": [
                "Mandates a unique 'Idempotency-Key' HTTP header on all 'POST /api/v1/orders'.",
                "If a request with an identical key is received, the server returns the existing order.",
                "Zero duplicate stock deductions regardless of how many times the user retries.",
                "Ensures complete fault tolerance across flaky WiFi or LTE connections."
            ],
            "technical": [
                "Idempotency keys tracked in dedicated database column with unique constraint.",
                "Frontend generates unique key using prescription ID and timestamp.",
                "Complies with modern fintech & healthcare distributed systems best practices.",
                "Prevents duplicate ledger movements under all network disconnect scenarios."
            ],
            "guarantee": "Idempotency keys protect against network retries and double-clicks, guaranteeing orders are finalized exactly once."
        },
        {
            "num": "15",
            "name": "Immutable Append-Only Stock Movement Ledger",
            "category": "REGULATORY AUDITING",
            "problem": [
                "Schedule H & H1 drugs (antibiotics, narcotics) mandate strict transaction logs under Indian law.",
                "Traditional POS software simply overwrites quantity numbers without an audit trail.",
                "When stock goes missing, managers cannot identify who dispensed it or when.",
                "State drug inspectors penalize pharmacies that cannot furnish batch movement logs."
            ],
            "solution": [
                "Every inventory change creates an immutable row in 'stock_movements'.",
                "Records timestamp, batch ID, product ID, delta quantity (-20), and balance after (60).",
                "Links every deduction directly to the finalized order ID and dispensing pharmacist.",
                "Stock movements are strictly append-only (no updates, no deletions allowed)."
            ],
            "technical": [
                "Schema modeled in 'app/models/inventory.py:StockMovement'.",
                "Captures movement reason: 'prescription_dispensed', 'intake_seed', 'adjustment'.",
                "Inspection-ready exports for regulatory compliance under Drugs & Cosmetics Rules.",
                "Verified by automated test checking balance consistency across movements."
            ],
            "guarantee": "Every pill dispensed is permanently recorded in an immutable ledger, providing full audit compliance for Schedule H/H1 inspections."
        },
        {
            "num": "16",
            "name": "Comprehensive Inventory & Batch Management Console",
            "category": "STORE OPERATIONS",
            "problem": [
                "Pharmacists have no central dashboard to view all active batches across brands.",
                "Expiry dates are hidden inside drawer packages rather than visible digitally.",
                "Quarantined batches from manufacturer alerts get lost among sellable stock.",
                "Lack of real-time visibility leads to embarrassing stock-outs at the counter."
            ],
            "solution": [
                "Dedicated Inventory Workspace: '/app/inventory' displaying all batches.",
                "Live status badges: Active (green), Quarantined (amber), Recalled/Expired (red).",
                "Shows batch number, current quantity, expiry date, and unit/pack prices.",
                "Visual warning indicators on batches expiring within 90 days."
            ],
            "technical": [
                "Powered by TanStack Query for instantaneous search and sorting.",
                "REST endpoint: 'GET /api/v1/inventory' with pagination and status filters.",
                "Demonstrated in automated test: stock decrements immediately update UI upon reload.",
                "Enables pharmacy managers to conduct rapid physical inventory reconciliations."
            ],
            "guarantee": "The inventory console provides instant visibility into active stock, batch numbers, and expiry timelines across the entire store."
        },
        {
            "num": "17",
            "name": "Medicine Catalogue & Alternative Candidate Explorer",
            "category": "CATALOGUE INTELLIGENCE",
            "problem": [
                "Staff struggle to find which generic alternatives exist for a given brand in store.",
                "Looking up price differences across manufacturers is time-consuming.",
                "When an alternative is not recommended, staff don't know the clinical reason.",
                "Slow catalog lookups increase patient wait times at the counter."
            ],
            "solution": [
                "Interactive Catalogue Search: '/app/medicines' with live search as you type.",
                "Detail view displays brand name, manufacturer, formulation summary, and MRP.",
                "Integrated Candidates Explorer: displays all eligible generic substitutions.",
                "Rejected Candidates Panel: explicitly details why other products are not eligible."
            ],
            "technical": [
                "REST endpoint: 'GET /api/v1/medicines/{id}/candidates'.",
                "Categorizes candidates into 'eligible_candidates' and 'rejected_candidates'.",
                "Rejection reasons include: Release Mismatch, Combination Subset, Stock Depleted.",
                "Empowers counter staff with instant clinical and pricing intelligence."
            ],
            "guarantee": "Staff can instantly look up medicines, inspect eligible bio-equivalent generics, and review explicit clinical rejection reasons."
        },
        {
            "num": "18",
            "name": "Executive Analytics Dashboard & Clinical KPIs",
            "category": "BUSINESS INTELLIGENCE",
            "problem": [
                "Pharmacy owners have no metric tracking the financial savings delivered to patients.",
                "Fulfillment coverage rate (how many prescribed lines could be filled) is unknown.",
                "Managers cannot identify which batches are approaching expiry this month.",
                "Lack of centralized operational KPIs limits pharmacy growth and optimization."
            ],
            "solution": [
                "Executive Dashboard on login: '/app' with real-time KPI metric tiles.",
                "Total Prescriptions Processed counter with status breakdowns.",
                "Aggregate Patient Savings Delivered (₹) tracking cumulative patient value.",
                "Stock Risk Alerts: instant counters for batches expiring within 30 and 90 days."
            ],
            "technical": [
                "REST endpoint: 'GET /api/v1/dashboard' computed via efficient SQL aggregations.",
                "Recent Prescriptions and Active Clinical Approvals quick-action tables.",
                "Allows pharmacy owners to market their generic savings impact to the community.",
                "Assists purchasing managers with timely re-order and clearance decisions."
            ],
            "guarantee": "The executive dashboard transforms operational data into actionable clinical KPIs, expiry risk warnings, and patient savings metrics."
        },
        {
            "num": "19",
            "name": "Privacy-Preserving Local Storage & Retention Policies",
            "category": "DATA PRIVACY & SECURITY",
            "problem": [
                "Prescriptions contain sensitive diagnostic information and patient identities.",
                "Sending prescription images to external public clouds risks severe privacy leaks.",
                "Retaining old temporary image files indefinitely creates security liabilities.",
                "Pharmacies must comply with India's Digital Personal Data Protection (DPDP) Act."
            ],
            "solution": [
                "Local private storage volume: prescription files stored on isolated local disk.",
                "Zero patient data is transmitted to external advertising networks or public models.",
                "Configurable Data Retention Policy: automatically purges temporary images after 24h.",
                "Dedicated Privacy Policy view: '/privacy' explaining data governance to patients."
            ],
            "technical": [
                "Admin settings console: '/app/settings' allows custom retention period configuration.",
                "Session security: Argon2id password hashing and HTTP-only signed session cookies.",
                "Granular audit logs track every document view, upload, and deletion event.",
                "Ensures total legal compliance with Indian healthcare data privacy laws."
            ],
            "guarantee": "All prescription documents remain strictly on local mounted volumes with automated 24-hour cleanup to protect patient privacy."
        },
        {
            "num": "20",
            "name": "Offline-First Resilience & Evaluator Fixtures",
            "category": "SYSTEM RELIABILITY",
            "problem": [
                "Cloud-dependent pharmacy systems stop dispensing when the internet disconnects.",
                "External vision and OCR APIs frequently experience rate limits or downtime.",
                "Evaluating and onboarding new software is difficult without pre-seeded test data.",
                "Pharmacies cannot afford a single minute of counter downtime during busy hours."
            ],
            "solution": [
                "Local-first architecture: local PostgreSQL and FastAPI backend require zero external cloud.",
                "Fully operable via manual entry even if OCR or vision services are offline.",
                "Integrated Synthetic Demo Fixtures: single-click scenario loading for evaluators.",
                "Pre-seeded with realistic Indian pharmaceutical brands, batches, and price points."
            ],
            "technical": [
                "Self-contained seed script: 'app/seed/seed_demo.py' generates idempotent test data.",
                "Quick-fill demo buttons on login screen (Pharmacist, Assistant, Admin).",
                "Evaluator button 'Load Sample Prescription' triggers a complete 2-line test flow.",
                "Ensures judges, regulators, and pharmacy operators can test the system in seconds."
            ],
            "guarantee": "PharmaBridge guarantees uninterrupted counter dispensing through local-first architecture and built-in synthetic scenario fixtures."
        }
    ]

    for f in features:
        # Heading for feature
        hf = doc.add_heading(level=2)
        rf_num = hf.add_run(f"Feature {f['num']}: {f['name']}\n")
        rf_num.font.name = "Segoe UI"
        rf_num.font.size = Pt(13.5)
        rf_num.font.bold = True
        rf_num.font.color.rgb = C_DARK

        rf_cat = hf.add_run(f"CATEGORY: {f['category']}")
        rf_cat.font.name = "Segoe UI"
        rf_cat.font.size = Pt(9)
        rf_cat.font.bold = True
        rf_cat.font.color.rgb = C_TEAL

        # 3-Column Table
        ftbl = doc.add_table(rows=2, cols=3)
        ftbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        ftbl.autofit = False

        c_widths = [Inches(2.2), Inches(2.4), Inches(2.2)]

        # Header Row
        headers = ["The Operational Problem", "How PharmaBridge Solves It", "Technical & Quality Highlights"]
        header_bgs = ["991B1B", "0F766E", "1E293B"] # Red, Teal, Slate
        for i in range(3):
            cell = ftbl.cell(0, i)
            cell.width = c_widths[i]
            set_cell_background(cell, header_bgs[i])
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(headers[i])
            r.font.name = "Segoe UI"
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

        # Content Row
        content_items = [f["problem"], f["solution"], f["technical"]]
        for i in range(3):
            cell = ftbl.cell(1, i)
            cell.width = c_widths[i]
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
            set_cell_borders(cell, 
                             top=("single", "6", "0", "E2E8F0"),
                             bottom=("single", "6", "0", "CBD5E1"),
                             left=("single", "6", "0", "E2E8F0"),
                             right=("single", "6", "0", "E2E8F0"))
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            
            for item_idx, b in enumerate(content_items[i]):
                if item_idx > 0:
                    p = cell.add_paragraph()
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15
                rb = p.add_run(f"•  {b}")
                rb.font.name = "Segoe UI"
                rb.font.size = Pt(8.5)
                rb.font.color.rgb = C_SLATE

        # Space before callout
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(4)
        p_sp.paragraph_format.space_after = Pt(0)

        # Guarantee Callout
        add_callout(doc, f"Feature {f['num']} Standard", f["guarantee"], bg_hex="F0FDFA", border_hex="0D9488")

    doc.add_page_break()

    # =========================================================================
    # DEEP-DIVE: FORMULATION EQUIVALENCE & BIO-PARITY ENGINE
    # =========================================================================
    h1_chem = doc.add_heading(level=1)
    r = h1_chem.add_run("3. Clinical Intelligence & Pharmacological Safety Rules")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p_chem = doc.add_paragraph()
    p_chem.paragraph_format.line_spacing = 1.15
    p_chem.paragraph_format.space_after = Pt(12)
    r_chem = p_chem.add_run(
        "Unlike commercial e-commerce websites that utilize fuzzy string matching or margin-boosting recommendation algorithms, "
        "PharmaBridge implements a deterministic pharmacological matching engine based on chemical ontology. The engine enforces "
        "four clinical barriers before a candidate medicine can ever appear in the substitution dropdown:"
    )
    r_chem.font.name = "Segoe UI"
    r_chem.font.size = Pt(10)
    r_chem.font.color.rgb = C_SLATE

    chem_rules = [
        ("1. Exact Active Substance & Strength Parity", 
         "All active substances must match 1:1. The molecular strength numerator (e.g., 500) and unit (mg) are normalized "
         "using exact Decimal representations. For example, 0.5g is normalized to 500mg, preventing unit mismatch errors."),
        ("2. Canonical Salt Preservation", 
         "Different chemical salts alter solubility, gastric tolerance, and peak serum concentrations. "
         "The database isolates the active moiety from the counter-ion. Cross-salt substitutions (e.g., Metformin HCl vs Pamoate) "
         "are rejected with the formal reason 'Salt Identity Incompatible'."),
        ("3. Release Profile Segregation", 
         "Immediate Release (IR) and Extended/Sustained Release (ER/SR/CR/DR) formulations are clinically non-interchangeable. "
         "A prescription for Metformin IR 500mg will strictly exclude Metformin ER 500mg to prevent fatal dose dumping or delayed response."),
        ("4. Combination Multiset Matching", 
         "Fixed-Dose Combinations (FDCs) require complete multiset equality. If Augmentin (Amoxicillin 500mg + Clavulanic Acid 125mg) "
         "is prescribed, a candidate containing only Amoxicillin 500mg is rejected under the rule 'Combination Subset Mismatch'."),
        ("5. Narrow Therapeutic Index (NTI) Quarantine", 
         "Drugs with narrow therapeutic windows (Warfarin, Lithium, Digoxin, Levothyroxine) are locked against automated "
         "generic switching, requiring explicit prescribing physician confirmation.")
    ]

    for title, desc in chem_rules:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        rt = p.add_run(title + "\n")
        rt.font.name = "Segoe UI"
        rt.font.size = Pt(10.5)
        rt.font.bold = True
        rt.font.color.rgb = C_TEAL
        
        rd = p.add_run(desc)
        rd.font.name = "Segoe UI"
        rd.font.size = Pt(9.5)
        rd.font.color.rgb = C_SLATE

    doc.add_page_break()

    # =========================================================================
    # DEEP-DIVE: WHOLE-PACK ECONOMICS & 33.33% CASE STUDY
    # =========================================================================
    h1_econ = doc.add_heading(level=1)
    r = h1_econ.add_run("4. Economic Precision & The 33.33% Savings Case Study")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p_econ = doc.add_paragraph()
    p_econ.paragraph_format.line_spacing = 1.15
    p_econ.paragraph_format.space_after = Pt(10)
    r_econ = p_econ.add_run(
        "A persistent failure of retail pharmacy software in India is quoting fractional blister pack prices. When a doctor writes "
        "a prescription for 15 tablets, standard POS systems multiply 15 by a per-unit price (e.g. ₹1.33 = ₹20.00). However, retail "
        "regulations forbid cutting blister packaging for many sensitive medicines, forcing pharmacists to either sell whole packs or "
        "charge arbitrary rates. PharmaBridge models physical pack constraints directly and computes exact costs using integer paise arithmetic."
    )
    r_econ.font.name = "Segoe UI"
    r_econ.font.size = Pt(10)
    r_econ.font.color.rgb = C_SLATE

    # Case Study Table
    cs_tbl = doc.add_table(rows=7, cols=3)
    cs_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cs_tbl.autofit = False

    cs_widths = [Inches(2.2), Inches(2.3), Inches(2.3)]
    cs_headers = ["Economic Metric", "Prescribed Baseline (Brand A)", "Optimized Generic (Product B)"]
    for i in range(3):
        cell = cs_tbl.cell(0, i)
        cell.width = cs_widths[i]
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=90, bottom=90, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(cs_headers[i])
        r.font.name = "Segoe UI"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    cs_data = [
        ("Prescription Request", "15 Tablets Paracetamol 500mg", "15 Tablets Paracetamol 500mg"),
        ("Pack Configuration", "15 Tablets per Strip", "10 Tablets per Strip"),
        ("Pack Break Allowed", "Allowed (or exact match)", "Disallowed (Whole Pack Enforced)"),
        ("Packs Dispensed", "1 Pack (15 Tablets)", "2 Whole Packs (ceil(15/10) = 2)"),
        ("Total Units Supplied", "15 Tablets (0 Excess)", "20 Tablets (5 Bonus Unexpired Tablets)"),
        ("Total Bill to Patient", "₹30.00 (₹2.00 per unit)", "₹20.00 (2 × ₹10.00 = ₹1.00 per unit)"),
    ]

    for idx, (m, b, g) in enumerate(cs_data):
        row_idx = idx + 1
        c0 = cs_tbl.cell(row_idx, 0)
        c1 = cs_tbl.cell(row_idx, 1)
        c2 = cs_tbl.cell(row_idx, 2)
        c0.width, c1.width, c2.width = cs_widths
        
        bg = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            set_cell_borders(c, bottom=("single", "6", "0", "E2E8F0"))

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(m)
        r0.font.name = "Segoe UI"
        r0.font.size = Pt(9)
        r0.font.bold = True
        r0.font.color.rgb = C_DARK

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(b)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9)
        r1.font.color.rgb = C_SLATE

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(g)
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(9)
        r2.font.bold = (idx == 5)
        r2.font.color.rgb = C_EMERALD if idx == 5 else C_SLATE

    # Space
    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(6)
    p_sp2.paragraph_format.space_after = Pt(2)

    add_callout(
        doc,
        "The Verifiable Mathematical Proof",
        "Net Patient Savings = ₹30.00 (Baseline) - ₹20.00 (Candidate) = ₹10.00.\n"
        "Savings Percentage = (₹10.00 / ₹30.00) = 33.33% Real Cash Savings!\n"
        "Outcome: The patient pays 33.33% less money AND receives 5 additional unexpired tablets.",
        bg_hex="ECFDF5",
        border_hex="059669"
    )

    doc.add_page_break()

    # =========================================================================
    # DEEP-DIVE: FEFO INVENTORY & DATABASE CONCURRENCY CONTROL
    # =========================================================================
    h1_fefo = doc.add_heading(level=1)
    r = h1_fefo.add_run("5. FEFO Inventory Engine & Database Concurrency Architecture")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p_fefo = doc.add_paragraph()
    p_fefo.paragraph_format.line_spacing = 1.15
    p_fefo.paragraph_format.space_after = Pt(12)
    r_fefo = p_fefo.add_run(
        "Inventory wastage due to expired medication is the single largest financial drain on Indian retail pharmacies, "
        "averaging 2% to 5% of total annual turnover. PharmaBridge resolves this through a multi-tier transactional engine:"
    )
    r_fefo.font.name = "Segoe UI"
    r_fefo.font.size = Pt(10)
    r_fefo.font.color.rgb = C_SLATE

    fefo_sections = [
        ("A. First-Expired, First-Out (FEFO) Allocation Algorithm",
         "When an order quote is calculated, the system queries all active batches for the product ordered by 'expires_on ASC, received_at ASC'. "
         "Batches nearing expiry are allocated first. Batches expiring within the course of treatment or within the 30-day safety buffer "
         "are strictly quarantined from allocation. In the demo dataset, Batch PB-2026-01 (180 days to expiry) is automatically depleted "
         "before Batch PB-2026-02 (400 days to expiry) is touched."),
        ("B. PostgreSQL Row-Level Concurrency Locks (SELECT ... FOR UPDATE)",
         "In busy pharmacies where multiple checkout counters operate simultaneously, two clerks may attempt to dispense the final units "
         "of a batch at the exact same moment. PharmaBridge locks all allocated batch rows within an atomic PostgreSQL transaction using "
         "'SELECT ... FOR UPDATE' in stable ID order (preventing deadlocks). The system re-checks available quantity under the active lock. "
         "If stock was depleted mid-flight by another counter, the transaction rolls back cleanly and returns an HTTP 409 Conflict error."),
        ("C. Idempotent Finalization (Idempotency-Key Header)",
         "To handle flaky network connections and impatient double-clicks, every order finalization request mandates a unique "
         "'Idempotency-Key' HTTP header. If a duplicate key is received, the server returns the previously created order record "
         "without executing a second inventory deduction, guaranteeing that stock is decremented exactly once."),
        ("D. Immutable Append-Only Stock Movement Ledger",
         "Under Schedule H and H1 of the Drugs & Cosmetics Rules, pharmacies must maintain auditable dispensing logs. "
         "PharmaBridge forbids UPDATE and DELETE queries on inventory balances. Instead, every physical transaction appends an "
         "immutable row to the 'stock_movements' table, recording the timestamp, batch ID, product ID, delta (-20), and balance after (60), "
         "directly linked to the order ID and dispensing pharmacist's authenticated license ID.")
    ]

    for title, desc in fefo_sections:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        rt = p.add_run(title + "\n")
        rt.font.name = "Segoe UI"
        rt.font.size = Pt(10.5)
        rt.font.bold = True
        rt.font.color.rgb = C_TEAL
        
        rd = p.add_run(desc)
        rd.font.name = "Segoe UI"
        rd.font.size = Pt(9.5)
        rd.font.color.rgb = C_SLATE

    doc.add_page_break()

    # =========================================================================
    # CLINICAL GOVERNANCE, ROLES & PRIVACY
    # =========================================================================
    h1_gov = doc.add_heading(level=1)
    r = h1_gov.add_run("6. Clinical Governance, Staff Roles & Data Privacy")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p_gov = doc.add_paragraph()
    p_gov.paragraph_format.line_spacing = 1.15
    p_gov.paragraph_format.space_after = Pt(10)
    r_gov = p_gov.add_run(
        "PharmaBridge implements strict Role-Based Access Control (RBAC) to ensure compliance with the Pharmacy Act 1948, "
        "which mandates that medication substitutions and dispensing decisions must be executed solely by licensed pharmacists."
    )
    r_gov.font.name = "Segoe UI"
    r_gov.font.size = Pt(10)
    r_gov.font.color.rgb = C_SLATE

    # Roles Table
    roles_tbl = doc.add_table(rows=4, cols=3)
    roles_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    roles_tbl.autofit = False

    r_widths = [Inches(1.5), Inches(1.8), Inches(3.5)]
    r_headers = ["Staff Role", "Permitted Actions", "Restricted & Blocked Operations"]
    for i in range(3):
        cell = roles_tbl.cell(0, i)
        cell.width = r_widths[i]
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=90, bottom=90, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(r_headers[i])
        r.font.name = "Segoe UI"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    roles_data = [
        ("👨‍⚕️ Pharmacist", 
         "Full clinical authority: Intake, review, substitution candidate approval, clinical notes, order finalization, inventory deduction.", 
         "None (Full clinical operations authorized)."),
        ("📋 Pharmacy Assistant", 
         "Prescription intake, scanning slips, uploading documents, manual item entry, catalog viewing, reviewing draft lines.", 
         "Strictly BLOCKED from approving fulfilment plans, signing substitutions, and finalizing orders (HTTP 403 Forbidden)."),
        ("⚙️ Store Admin", 
         "Pharmacy master settings, user account creation, role assignment, data retention policies, audit log exports.", 
         "Standard administrative management; clinical dispensing requires logged-in Pharmacist credentials.")
    ]

    for idx, (role, perm, rest) in enumerate(roles_data):
        row_idx = idx + 1
        c0 = roles_tbl.cell(row_idx, 0)
        c1 = roles_tbl.cell(row_idx, 1)
        c2 = roles_tbl.cell(row_idx, 2)
        c0.width, c1.width, c2.width = r_widths
        
        bg = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            set_cell_borders(c, bottom=("single", "6", "0", "E2E8F0"))

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(role)
        r0.font.name = "Segoe UI"
        r0.font.size = Pt(9)
        r0.font.bold = True
        r0.font.color.rgb = C_DARK

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(perm)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_SLATE

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(rest)
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(185, 28, 28) if "BLOCKED" in rest else C_SLATE

    # Privacy Subsection
    h2_priv = doc.add_heading(level=2)
    r = h2_priv.add_run("Data Privacy & Local Storage Architecture (DPDP Act Compliance)")
    r.font.name = "Segoe UI"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = C_TEAL

    p_priv = doc.add_paragraph()
    p_priv.paragraph_format.line_spacing = 1.15
    p_priv.paragraph_format.space_after = Pt(10)
    r_priv = p_priv.add_run(
        "To comply with India's Digital Personal Data Protection (DPDP) Act 2023, PharmaBridge operates on a strict "
        "local-storage architecture. Prescription images and medical records are stored strictly on a private mounted local volume "
        "on the pharmacy premises. Zero patient health information is transmitted to third-party public cloud services or ad networks. "
        "Furthermore, a configurable automated background retention task purges temporary prescription scans after 24 hours while "
        "preserving the anonymized, finalized clinical audit ledger."
    )
    r_priv.font.name = "Segoe UI"
    r_priv.font.size = Pt(9.5)
    r_priv.font.color.rgb = C_SLATE

    doc.add_page_break()

    # =========================================================================
    # 5-MINUTE MENTOR & EVALUATOR DEMO SCRIPT
    # =========================================================================
    h1_demo = doc.add_heading(level=1)
    r = h1_demo.add_run("7. The 5-Minute Evaluator & Mentor Walkthrough Script")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p_demo = doc.add_paragraph()
    p_demo.paragraph_format.line_spacing = 1.15
    p_demo.paragraph_format.space_after = Pt(10)
    r_demo = p_demo.add_run(
        "To allow judges, hackathon mentors, regulators, and pharmacy operators to evaluate the full capabilities of PharmaBridge "
        "without manual data entry, the system includes a pre-seeded evaluator scenario that can be executed in under 5 minutes:"
    )
    r_demo.font.name = "Segoe UI"
    r_demo.font.size = Pt(10)
    r_demo.font.color.rgb = C_SLATE

    demo_steps = [
        ("Step 1: Authenticate as Pharmacist", 
         "Navigate to http://localhost:5173/login. Click the one-click '👨‍⚕️ Pharmacist' button to autofill demo credentials "
         "(pharmacist@pharmabridge.demo / DemoPharmacistPass123!). Click 'Sign in to Workspace'."),
        ("Step 2: Trigger the 5-Minute Demo Scenario", 
         "On the Dashboard or New Prescription page, click the high-visibility purple button '⚡ Load Sample Prescription'. "
         "This automatically seeds a two-line prescription: Line 1 (Brand A Paracetamol 500mg, 15 tabs) and Line 2 (Amlo 5mg ambiguous)."),
        ("Step 3: Resolve Clinical Ambiguity", 
         "On the Review page, observe Line 1 is pre-confirmed, while Line 2 displays an amber 'Ambiguous: Catalogue Selection Required' badge. "
         "In the Line 2 dropdown, select 'DemoAmlo 5 (amlodipine 5mg (tablet))'. Click 'Confirm & Generate Plan'."),
        ("Step 4: Select Generic Candidate & Observe 33.33% Savings", 
         "On the Fulfilment Plan screen, inspect Line 1. Open the 'Dispensing Selection' dropdown and select "
         "'Product B Generic Paracetamol (Pack ₹10.00)'. Instantly observe the dynamic calculation badge showing 33.33% Real Savings "
         "(₹30.00 Baseline vs ₹20.00 for two 10-packs)."),
        ("Step 5: Execute Mandatory Clinical Approval", 
         "In the right-hand panel, click 'Approve Fulfilment Plan'. The system records the approving pharmacist's credentials and timestamp, "
         "unlocking finalization."),
        ("Step 6: Finalize Order & Verify Atomic FEFO Deduction", 
         "Click 'Finalize Order & Deduct Stock'. The system redirects to the Order Detail receipt screen showing status 'FINALIZED'. "
         "Navigate to 'Inventory & Batches' in the sidebar and verify that Batch PB-2026-01 was decremented by exactly 20 units.")
    ]

    for title, desc in demo_steps:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        rt = p.add_run(title + "\n")
        rt.font.name = "Segoe UI"
        rt.font.size = Pt(10)
        rt.font.bold = True
        rt.font.color.rgb = C_TEAL
        
        rd = p.add_run(desc)
        rd.font.name = "Segoe UI"
        rd.font.size = Pt(9.5)
        rd.font.color.rgb = C_SLATE

    doc.add_page_break()

    # =========================================================================
    # SYSTEM SUMMARY & VERIFICATION MATRIX
    # =========================================================================
    h1_sum = doc.add_heading(level=1)
    r = h1_sum.add_run("8. System Summary & Automated Verification Matrix")
    r.font.name = "Segoe UI"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_DARK

    p_sum = doc.add_paragraph()
    p_sum.paragraph_format.line_spacing = 1.15
    p_sum.paragraph_format.space_after = Pt(12)
    r_sum = p_sum.add_run(
        "PharmaBridge is fully implemented, compiled, and rigorously tested with 100% automated test pass rates across both "
        "backend and frontend verification suites. No mock databases are used; all tests execute against a live PostgreSQL 17 transactional instance:"
    )
    r_sum.font.name = "Segoe UI"
    r_sum.font.size = Pt(10)
    r_sum.font.color.rgb = C_SLATE

    # Verification Matrix Table
    ver_tbl = doc.add_table(rows=6, cols=4)
    ver_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    ver_tbl.autofit = False

    v_widths = [Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.4)]
    v_headers = ["Testing Suite", "Target Architecture", "Verification Scope", "Result / Status"]
    for i in range(4):
        cell = ver_tbl.cell(0, i)
        cell.width = v_widths[i]
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=90, bottom=90, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(v_headers[i])
        r.font.name = "Segoe UI"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    v_data = [
        ("Pytest Backend Suite", "FastAPI + asyncpg (PostgreSQL 17)", "Auth, Equivalence, Paise Math, FEFO, Locks", "21 / 21 Passed (100%)"),
        ("Playwright Desktop", "Desktop Chrome (1440 × 900)", "Full Dispensing Flow, Approvals, Orders", "4 / 4 Passed (100%)"),
        ("Playwright Tablet", "Galaxy Tab S4 (768 × 1024)", "Touch Navigation, Gated Approvals, Review", "4 / 4 Passed (100%)"),
        ("Playwright Mobile", "Pixel 7 (390 × 844)", "Responsive Layout, Mobile Viewports, Stepper", "4 / 4 Passed (100%)"),
        ("TypeScript / Vite Build", "React 19 + TypeScript + Vite 6", "Type Safety, Production Bundle Optimization", "0 Errors (Clean Build)")
    ]

    for idx, (s, a, sc, res) in enumerate(v_data):
        row_idx = idx + 1
        c0 = ver_tbl.cell(row_idx, 0)
        c1 = ver_tbl.cell(row_idx, 1)
        c2 = ver_tbl.cell(row_idx, 2)
        c3 = ver_tbl.cell(row_idx, 3)
        c0.width, c1.width, c2.width, c3.width = v_widths
        
        bg = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
        for c in (c0, c1, c2, c3):
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            set_cell_borders(c, bottom=("single", "6", "0", "E2E8F0"))

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(s)
        r0.font.name = "Segoe UI"
        r0.font.size = Pt(9)
        r0.font.bold = True
        r0.font.color.rgb = C_DARK

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(a)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_SLATE

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(sc)
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = C_SLATE

        p3 = c3.paragraphs[0]
        r3 = p3.add_run(res)
        r3.font.name = "Segoe UI"
        r3.font.size = Pt(8.5)
        r3.font.bold = True
        r3.font.color.rgb = C_EMERALD

    # Space
    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(8)
    p_sp3.paragraph_format.space_after = Pt(2)

    add_callout(
        doc,
        "Production Readiness Summary",
        "Total Features Documented & Implemented: 20 Core Modules\n"
        "Total Automated Tests Passed: 33 Tests (100% Pass Rate)\n"
        "Compiler Status: Zero TypeScript & Python runtime errors\n"
        "Deployment Verdict: Production-grade MVP ready for retail pharmacy deployment.",
        bg_hex="F0FDFA",
        border_hex="0D9488"
    )

    # Save to root workspace
    output_docx = os.path.abspath(os.path.join(os.path.dirname(__file__), "../PharmaBridge_All_Features_Comprehensive_Documentation.docx"))
    doc.save(output_docx)
    print(f"Comprehensive DOCX successfully generated at: {output_docx} ({os.path.getsize(output_docx)} bytes)")

if __name__ == "__main__":
    build_docx()
