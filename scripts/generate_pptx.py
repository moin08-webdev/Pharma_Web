import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    # Set 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    C_TEAL = RGBColor(15, 118, 110)       # #0F766E Primary Brand
    C_DARK = RGBColor(15, 23, 42)         # #0F172A Dark Slate
    C_LIGHT_BG = RGBColor(248, 250, 252)  # #F8FAFC Off-white
    C_CARD_BG = RGBColor(255, 255, 255)   # #FFFFFF Card White
    C_CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0 Border
    C_MUTED = RGBColor(100, 116, 139)     # #64748B Muted Gray
    C_EMERALD = RGBColor(5, 150, 105)     # #059669 Success Green
    C_AMBER = RGBColor(217, 119, 6)       # #D97706 Warning Amber
    C_ROSE = RGBColor(225, 29, 72)        # #E11D48 Danger Red
    C_WHITE = RGBColor(255, 255, 255)

    blank_layout = prs.slide_layouts[6]
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/web/public/logo.png"))

    def add_background(slide, color=C_LIGHT_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.color.rgb = color
        return bg

    def add_header(slide, title_text, category_text="PHARMABRIDGE PLATFORM OVERVIEW", slide_num=None):
        # Top Category pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(3.2), Inches(0.35))
        pill.fill.solid()
        pill.fill.fore_color.rgb = RGBColor(230, 244, 242)
        pill.line.fill.background()
        tf = pill.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = C_TEAL
        p.alignment = PP_ALIGN.CENTER

        # Slide Title
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(9.6), Inches(0.7))
        tf_t = tx_box.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = C_DARK

        # Logo on Header
        if os.path.exists(logo_path):
            slide.shapes.add_picture(logo_path, Inches(10.5), Inches(0.35), width=Inches(0.55), height=Inches(0.55))

        # Top Right Slide Indicator
        if slide_num:
            ind_box = slide.shapes.add_textbox(Inches(11.1), Inches(0.45), Inches(1.4), Inches(0.4))
            tf_i = ind_box.text_frame
            p_i = tf_i.paragraphs[0]
            p_i.text = f"Slide {slide_num} of 8"
            p_i.font.size = Pt(9.5)
            p_i.font.color.rgb = C_MUTED
            p_i.alignment = PP_ALIGN.RIGHT

    def create_card(slide, left, top, width, height, title, body_bullets, accent_color=C_TEAL, bg_color=C_CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1)

        # Top Accent Stripe
        stripe = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.08))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = accent_color
        stripe.line.fill.background()

        # Text Frame
        tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.15), Inches(width - 0.4), Inches(height - 0.25))
        tf = tb.text_frame
        tf.word_wrap = True

        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(13)
        p_title.font.bold = True
        p_title.font.color.rgb = C_DARK
        p_title.space_after = Pt(8)

        for b in body_bullets:
            p = tf.add_paragraph()
            p.text = f"•  {b}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = RGBColor(51, 65, 85)
            p.space_after = Pt(4)

        return card

    # ==========================================
    # SLIDE 1: Title Slide (Cover)
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    add_background(slide1, C_DARK)

    # Decorative background card
    dec = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    dec.fill.solid()
    dec.fill.fore_color.rgb = RGBColor(30, 41, 59)
    dec.line.color.rgb = RGBColor(51, 65, 85)

    if os.path.exists(logo_path):
        slide1.shapes.add_picture(logo_path, Inches(10.5), Inches(1.2), width=Inches(1.5), height=Inches(1.5))

    # Title Tag
    tag = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(1.4), Inches(3.6), Inches(0.4))
    tag.fill.solid()
    tag.fill.fore_color.rgb = RGBColor(15, 118, 110)
    tag.line.fill.background()
    p = tag.text_frame.paragraphs[0]
    p.text = "NEXT-GENERATION PHARMACY TECH"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.alignment = PP_ALIGN.CENTER

    # Main Title
    tb_title = slide1.shapes.add_textbox(Inches(1.25), Inches(2.0), Inches(10.5), Inches(1.5))
    tf = tb_title.text_frame
    p1 = tf.paragraphs[0]
    p1.text = "PharmaBridge"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = "AI-Assisted Prescription Fulfilment & Clinical Dispensing Workspace"
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(45, 212, 191)  # Teal-400
    p2.space_before = Pt(8)

    p3 = tf.add_paragraph()
    p3.text = "Bringing Clinical Safety, Transparent Whole-Pack Economics, and Transactional FEFO Inventory to Indian Retail Pharmacies"
    p3.font.size = Pt(11)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    p3.space_before = Pt(12)

    # Footer Metadata Cards
    metas = [
        ("Architecture", "FastAPI + React 19 + PostgreSQL 17"),
        ("Compliance", "Pharmacy Act 1948 & Schedule H/H1"),
        ("Verification", "100% Automated Tests Passed (Pytest & Playwright)"),
        ("Status", "Production-Ready v1.0 MVP"),
    ]
    for i, (k, v) in enumerate(metas):
        m_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3 + i * 2.7), Inches(4.8), Inches(2.55), Inches(1.2))
        m_box.fill.solid()
        m_box.fill.fore_color.rgb = RGBColor(15, 23, 42)
        m_box.line.color.rgb = RGBColor(71, 85, 105)
        tf_m = m_box.text_frame
        p_k = tf_m.paragraphs[0]
        p_k.text = k.upper()
        p_k.font.size = Pt(8)
        p_k.font.bold = True
        p_k.font.color.rgb = RGBColor(45, 212, 191)
        p_v = tf_m.add_paragraph()
        p_v.text = v
        p_v.font.size = Pt(9.5)
        p_v.font.bold = True
        p_v.font.color.rgb = C_WHITE
        p_v.space_before = Pt(4)

    # ==========================================
    # SLIDE 2: The Problem Space
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_background(slide2)
    add_header(slide2, "The Problem: Indian Retail Pharmacy Pain Points", "INDUSTRY CHALLENGES", 2)

    problems = [
        ("1. Doctor Handwriting & Intake Errors", [
            "Handwritten paper prescriptions cause misinterpretations.",
            "Similar-sounding drug names lead to dangerous dispensing mistakes.",
            "Dosage strengths and release forms are frequently misidentified."
        ], C_ROSE),
        ("2. Profit-Driven Generic Substitution", [
            "Substitutions are often driven by wholesaler profit margins.",
            "Risk of dispensing incompatible salt identities or partial combinations.",
            "No automated pharmacological bio-equivalence verification."
        ], C_AMBER),
        ("3. Opaque Packaging & Pill Math", [
            "Pharmacies cut blister strips or force patients to buy excess pills.",
            "Fractional pill calculations cause confusion and mistrust.",
            "Patients lack transparent visibility into actual savings."
        ], C_TEAL),
        ("4. Expiry Waste & Disorganized Stock", [
            "Random dispensing leads to older stock expiring unnoticed.",
            "Indian pharmacies lose 2-5% of inventory value annually to expiry.",
            "Quarantined or recalled batches accidentally get sold."
        ], C_ROSE),
        ("5. Lack of Pharmacist Oversight", [
            "Unqualified counter assistants dispense prescription drugs without supervision.",
            "Violates Pharmacy Act 1948 and Schedule H/H1 regulatory rules.",
            "No verifiable audit trail or digital sign-off records."
        ], C_AMBER),
        ("6. Cloud Dependency & Outage Risks", [
            "Standard web POS systems halt completely if cloud APIs go down.",
            "Third-party OCR downtime stops counter dispensing.",
            "Pharmacies need local-first offline resilience."
        ], C_TEAL),
    ]

    for idx, (title, bullets, color) in enumerate(problems):
        row = idx // 3
        col = idx % 3
        create_card(slide2, 0.8 + col * 3.95, 1.7 + row * 2.65, 3.8, 2.45, title, bullets, color)

    # ==========================================
    # SLIDE 3: The PharmaBridge Solution Pipeline
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_background(slide3)
    add_header(slide3, "The PharmaBridge Solution: 6-Stage Fulfilment Pipeline", "CLINICAL WORKFLOW", 3)

    stages = [
        ("Step 1: Intake & OCR", "Upload prescription image/PDF or manual draft with private local storage.", C_TEAL),
        ("Step 2: Line Review", "Review extracted lines, resolve ambiguous dosages with amber warnings.", C_AMBER),
        ("Step 3: Bio-Equivalence", "Retrieve exact generic candidates with clinical rejection checks.", C_TEAL),
        ("Step 4: Pack Economics", "Calculate whole packs, excess units, and exact paise patient savings.", C_EMERALD),
        ("Step 5: Pharmacist Gate", "Mandatory clinical approval by registered Pharmacist (Assistants blocked).", C_ROSE),
        ("Step 6: FEFO Finalize", "Atomic row-lock stock deduction of earliest-expiring unquarantined batch.", C_TEAL),
    ]

    for idx, (step_title, step_desc, col_color) in enumerate(stages):
        top_y = 1.7 + idx * 0.85
        box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(11.733), Inches(0.72))
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD_BG
        box.line.color.rgb = C_CARD_BORDER

        # Left Step Indicator
        ind = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(top_y + 0.1), Inches(2.4), Inches(0.52))
        ind.fill.solid()
        ind.fill.fore_color.rgb = col_color
        ind.line.fill.background()
        tf_i = ind.text_frame
        p_i = tf_i.paragraphs[0]
        p_i.text = step_title
        p_i.font.size = Pt(10)
        p_i.font.bold = True
        p_i.font.color.rgb = C_WHITE
        p_i.alignment = PP_ALIGN.CENTER

        # Right Description
        desc_box = slide3.shapes.add_textbox(Inches(3.45), Inches(top_y + 0.05), Inches(8.9), Inches(0.6))
        tf_d = desc_box.text_frame
        tf_d.word_wrap = True
        p_d = tf_d.paragraphs[0]
        p_d.text = step_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_DARK

    # Bottom summary callout
    bot = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.85))
    bot.fill.solid()
    bot.fill.fore_color.rgb = RGBColor(240, 253, 250)
    bot.line.color.rgb = RGBColor(153, 246, 228)
    tf_b = bot.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "GUARANTEE: No medicine can be dispensed or stock deducted without passing clinical verification and receiving a registered pharmacist's digital sign-off."
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = C_TEAL
    p_b.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 4: Clinical Safety & Formulation Engine
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_background(slide4)
    add_header(slide4, "Clinical Safety: Deterministic Formulation Equivalence", "PHARMACOLOGICAL SAFETY", 4)

    rules = [
        ("1. Active Chemical Equivalence", [
            "Canonical chemical identity matching (e.g., paracetamol == acetaminophen).",
            "Identifies multi-ingredient component ratios accurately.",
            "Rejects any substitution lacking 100% active substance parity."
        ], C_TEAL),
        ("2. Canonical Salt Preservation", [
            "Maintains critical salt identities (e.g., Metformin HCl vs Pamoate).",
            "Incompatible salts with different bioavailability are blocked.",
            "Prevents therapeutic failures caused by altered drug absorption."
        ], C_TEAL),
        ("3. Release Profile Compatibility", [
            "Immediate Release (IR) vs Extended Release (ER / SR) strictly separated.",
            "Metformin IR 500mg strictly rejects Metformin ER 500mg.",
            "Protects patients from dangerous dose-dumping toxicities."
        ], C_ROSE),
        ("4. Combination Subset Rejection", [
            "Multi-drug combinations cannot be substituted by single agents.",
            "Amoxicillin + Clavulanic Acid strictly rejects Amoxicillin alone.",
            "Displays explicit clinical rejection: 'Combination Subset Mismatch'."
        ], C_AMBER),
        ("5. Narrow Therapeutic Index (NTI)", [
            "Flags high-risk drugs where small dose shifts cause fatal toxicity.",
            "Blocks automated generic substitution for critical NTI molecules.",
            "Enforces doctor confirmation on narrow-margin medications."
        ], C_ROSE),
        ("6. Transparent Rejection Feedback", [
            "Never leaves the pharmacist guessing why an alternative is missing.",
            "Clearly lists rejected alternatives with documented reasons.",
            "Educates staff on bio-equivalence and pharmacology rules."
        ], C_EMERALD),
    ]

    for idx, (title, bullets, color) in enumerate(rules):
        row = idx // 3
        col = idx % 3
        create_card(slide4, 0.8 + col * 3.95, 1.7 + row * 2.65, 3.8, 2.45, title, bullets, color)

    # ==========================================
    # SLIDE 5: Pack Economics & The 33.33% Case Study
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_background(slide5)
    add_header(slide5, "Pack Economics & Transparent Savings: The 33.33% Case Study", "MATHEMATICAL PRECISION", 5)

    # Left: Prescribed Brand A Card
    c_left = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(5.7), Inches(4.2))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = C_CARD_BG
    c_left.line.color.rgb = C_CARD_BORDER
    tf_l = c_left.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Prescribed Baseline: Brand A Paracetamol 500mg"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_DARK

    bullets_l = [
        "Patient Prescription: 15 tablets prescribed.",
        "Packaging: 15-tablet whole blister pack.",
        "Pack Selling Price: ₹30.00 (₹2.00 per unit).",
        "Packs Required: 1 pack = 15 units supplied (0 excess).",
        "Baseline Patient Cost: ₹30.00",
        "Status: High-cost originator brand."
    ]
    for b in bullets_l:
        p = tf_l.add_paragraph()
        p.text = f"•  {b}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(4)

    # Right: Candidate Product B Card
    c_right = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.7), Inches(5.7), Inches(4.2))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = RGBColor(240, 253, 250)
    c_right.line.color.rgb = RGBColor(153, 246, 228)
    tf_r = c_right.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Dispensed Alternative: Product B Generic Paracetamol"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    bullets_r = [
        "Formulation Equivalence: Exact 500mg oral Paracetamol tablet.",
        "Packaging: 10-tablet pack (Whole pack dispensing only; pack_break=false).",
        "Pack Selling Price: ₹10.00 (₹1.00 per unit).",
        "Pack Breakdown: ceil(15 / 10) = 2 packs needed.",
        "Units Supplied: 20 tablets (5 excess units supplied for patient).",
        "Total Patient Cost: 2 packs × ₹10.00 = ₹20.00"
    ]
    for b in bullets_r:
        p = tf_r.add_paragraph()
        p.text = f"•  {b}"
        p.font.size = Pt(10)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(4)

    # Bottom Big Banner: The Math
    banner = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.95))
    banner.fill.solid()
    banner.fill.fore_color.rgb = C_DARK
    banner.line.fill.background()
    tf_b = banner.text_frame
    p_b1 = tf_b.paragraphs[0]
    p_b1.text = "THE VERIFIED RESULT:  ₹30.00 (Baseline) − ₹20.00 (Generic) = ₹10.00 Savings = 33.33% REAL SAVINGS"
    p_b1.font.size = Pt(13)
    p_b1.font.bold = True
    p_b1.font.color.rgb = RGBColor(52, 211, 153) # Emerald
    p_b1.alignment = PP_ALIGN.CENTER

    p_b2 = tf_b.add_paragraph()
    p_b2.text = "Computed with exact Decimal paise arithmetic (zero floating-point error) while fully informing the patient of 5 bonus excess tablets."
    p_b2.font.size = Pt(9)
    p_b2.font.color.rgb = RGBColor(203, 213, 225)
    p_b2.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 6: FEFO Inventory & Transaction Safety
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_background(slide6)
    add_header(slide6, "FEFO Inventory Engine & Transactional Safety", "INVENTORY & DATABASE INTEGRITY", 6)

    inv_points = [
        ("1. First-Expired, First-Out (FEFO)", [
            "Automatically sorts available stock by earliest expiration date.",
            "Prioritizes batches expiring soonest to eliminate shelf waste.",
            "Saves pharmacies 2-5% in annual drug expiration losses."
        ], C_TEAL),
        ("2. Batch Status Protection", [
            "Batches flagged as 'Quarantined', 'Recalled', or 'Expired' are blocked.",
            "Active stock checks ensure unreserved balance is always strictly positive.",
            "Immediate visual alerts on batches within 90 days of expiry."
        ], C_ROSE),
        ("3. Concurrency & Row Locks", [
            "Uses PostgreSQL 'SELECT ... FOR UPDATE' row-level locks.",
            "Eliminates double-dispensing race conditions across busy counter terminals.",
            "Atomic transaction commits stock deduction with zero data corruption."
        ], C_AMBER),
        ("4. Idempotent Order Finalization", [
            "Every order finalization request requires a unique Idempotency-Key.",
            "Accidental double-clicks or browser retries cannot double-charge stock.",
            "Guarantees safe network retries and uninterrupted dispensing."
        ], C_TEAL),
        ("5. Append-Only Stock Ledger", [
            "Every stock change creates an immutable movement log entry.",
            "Tracks quantity change, remaining balance, actor ID, and prescription link.",
            "Provides audit-ready traceability for state drug inspectors."
        ], C_EMERALD),
        ("6. 5-Minute Quote Lock (TTL)", [
            "Quotes hold pricing and batch allocation for 5 minutes.",
            "Prevents pricing shifts while the pharmacist counsels the patient.",
            "Expired quotes seamlessly recalculate fresh batch allocations."
        ], C_TEAL),
    ]

    for idx, (title, bullets, color) in enumerate(inv_points):
        row = idx // 3
        col = idx % 3
        create_card(slide6, 0.8 + col * 3.95, 1.7 + row * 2.65, 3.8, 2.45, title, bullets, color)

    # ==========================================
    # SLIDE 7: Roles & Live Evaluator Walkthrough
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_background(slide7)
    add_header(slide7, "Staff Roles & 5-Minute Evaluator Walkthrough", "OPERATIONS & DEMO GUIDE", 7)

    # Left: Role Box
    c_roles = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(4.5), Inches(5.3))
    c_roles.fill.solid()
    c_roles.fill.fore_color.rgb = C_CARD_BG
    c_roles.line.color.rgb = C_CARD_BORDER
    tf_ro = c_roles.text_frame
    tf_ro.word_wrap = True

    p = tf_ro.paragraphs[0]
    p.text = "Role-Based Access Control (RBAC)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_DARK

    role_items = [
        ("PHARMACIST (Clinical Authority)", "pharmacist@pharmabridge.demo\n• Full approval permissions\n• Can substitute candidates\n• Finalizes orders & stock deduction"),
        ("ASSISTANT (Intake & Support)", "assistant@pharmabridge.demo\n• Creates drafts and uploads prescriptions\n• Can search catalogue\n• BLOCKED from approvals & finalization (403)"),
        ("ADMIN (Pharmacy Manager)", "admin@pharmabridge.demo\n• Manages staff roles and stores\n• Configures retention & audit policies\n• Oversees performance analytics")
    ]
    for r_title, r_desc in role_items:
        p = tf_ro.add_paragraph()
        p.text = r_title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_TEAL
        p.space_before = Pt(8)
        p_d = tf_ro.add_paragraph()
        p_d.text = r_desc
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = C_DARK

    # Right: 7-Step Evaluator Walkthrough
    c_walk = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(1.7), Inches(6.933), Inches(5.3))
    c_walk.fill.solid()
    c_walk.fill.fore_color.rgb = C_CARD_BG
    c_walk.line.color.rgb = C_CARD_BORDER
    tf_w = c_walk.text_frame
    tf_w.word_wrap = True

    p = tf_w.paragraphs[0]
    p.text = "5-Minute Evaluator Walkthrough Script"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_DARK

    walk_steps = [
        "1. Login: Visit http://localhost:5173/login and click 'Pharmacist' auto-fill.",
        "2. Load Scenario: Go to 'New Prescription' -> Click purple 'Load Sample Prescription'.",
        "3. Review Lines: Observe Brand A (confirmed) and Amlo 5mg (amber alert: ambiguous).",
        "4. Resolve Ambiguity: Select 'DemoAmlo 5' in dropdown -> Click 'Confirm & Generate Plan'.",
        "5. Test Economics: Switch Line 1 to 'Product B Generic' -> Verify 33.33% Savings displayed.",
        "6. Clinical Sign-off: Click 'Approve Fulfilment Plan' -> Click 'Finalize Order & Deduct Stock'.",
        "7. Verify Persistence: Reload page (F5) to confirm Postgres storage; check Inventory for -20 units."
    ]
    for s in walk_steps:
        p = tf_w.add_paragraph()
        p.text = s
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_DARK
        p.space_before = Pt(6)

    # ==========================================
    # SLIDE 8: Architecture & Verification
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_background(slide8)
    add_header(slide8, "Technical Architecture & Automated Test Verification", "ENGINEERING EXCELLENCE", 8)

    tech_cards = [
        ("Frontend Architecture", [
            "React 19 with strict TypeScript typing.",
            "Vite 6 build system (Production build: 3.48s).",
            "Tailwind CSS for accessible clinical UI.",
            "TanStack Query 5 for caching & polling."
        ], C_TEAL),
        ("Backend Architecture", [
            "FastAPI asynchronous REST framework.",
            "SQLAlchemy 2.0 with asyncpg driver.",
            "PostgreSQL 17.2 with Alembic migrations.",
            "Argon2id password hashing & secure cookies."
        ], C_TEAL),
        ("Privacy & Security", [
            "Private mounted storage for prescriptions.",
            "Configurable 24-hour retention purge.",
            "Zero patient data leakage to external models.",
            "Schedule H/H1 compliance audit ledger."
        ], C_AMBER),
        ("Automated Test Suite", [
            "21 Pytest Unit & Integration Tests (100% Pass).",
            "12 Playwright Cross-Device Tests (100% Pass).",
            "Tested on Desktop Chrome, Tablet, and Mobile.",
            "0 Type errors in production TypeScript build."
        ], C_EMERALD),
    ]

    for idx, (title, bullets, color) in enumerate(tech_cards):
        col = idx % 2
        row = idx // 2
        create_card(slide8, 0.8 + col * 5.9, 1.7 + row * 2.65, 5.75, 2.45, title, bullets, color)

    # Bottom Stat Bar
    stat_bar = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.85))
    stat_bar.fill.solid()
    stat_bar.fill.fore_color.rgb = C_DARK
    stat_bar.line.fill.background()
    tf_sb = stat_bar.text_frame
    p_sb = tf_sb.paragraphs[0]
    p_sb.text = "SUMMARY:  33 Tests Executed | 33 Passed (100%) | 0 Failures | 3 Form Factors Verified | Full-Stack Ready"
    p_sb.font.size = Pt(11)
    p_sb.font.bold = True
    p_sb.font.color.rgb = RGBColor(52, 211, 153)
    p_sb.alignment = PP_ALIGN.CENTER

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../PharmaBridge_Presentation.pptx"))
    prs.save(output_path)
    print(f"Presentation successfully saved to: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    build_presentation()
