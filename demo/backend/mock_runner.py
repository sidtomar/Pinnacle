"""
Mock pipeline runner — generates realistic content instantly for demo purposes.
No LLM API calls needed. Real runner can be swapped in for production.
"""
import time, random

# ── Pre-built mock content per topic keyword ──────────────────────────────────

MOCK_LIBRARY = {
    "GLP-1": {
        "title": "GLP-1 Receptor Agonists in Type 2 Diabetes: 2025 Real-World Evidence Update",
        "summary": (
            "A landmark 2025 meta-analysis of 34 RCTs (n=87,420) confirms GLP-1 receptor agonists "
            "deliver superior glycaemic control (HbA1c reduction: −1.8% vs −1.1% for DPP-4i) alongside "
            "significant cardiovascular and renal protection benefits. Semaglutide leads the class with "
            "the strongest evidence in South Asian T2DM populations, including three Indian cohort studies."
        ),
        "key_findings": [
            "Semaglutide 1 mg weekly reduces HbA1c by 1.8% and body weight by 6.2 kg at 52 weeks",
            "SUSTAIN-6 extension: 33% reduction in MACE vs placebo sustained at 5 years",
            "Dulaglutide shows superiority in patients with eGFR 30–60 (renal protection confirmed)",
            "Once-weekly formulations achieve 94% patient adherence vs 71% for daily injections",
            "Indian cohort (n=2,840): GLP-1 RAs reduce HbA1c by 1.6% in patients with BMI 23–27",
            "Combination with SGLT2 inhibitors provides additive CV and renal benefit",
        ],
        "clinical_insights": (
            "For Pinnacle Diabetologists: GLP-1 RAs are now first-line alongside metformin for T2DM "
            "patients with established ASCVD, heart failure, or CKD. The 2025 ADA/EASD consensus "
            "recommends semaglutide as preferred agent when weight reduction is also a goal. "
            "Key prescribing consideration for Indian patients: start at half the Western dose and "
            "titrate based on GI tolerability. Adherence counselling at week 4 significantly reduces "
            "discontinuation rates."
        ),
        "recommendations": [
            "Initiate GLP-1 RA in T2DM patients with HbA1c >7.5% and established CVD irrespective of baseline HbA1c",
            "Prefer semaglutide SC for maximum HbA1c lowering; oral semaglutide for injection-averse patients",
            "Combine with SGLT2i in heart failure or CKD patients for synergistic benefit",
            "Monitor for GI side effects in first 4 weeks; anti-emetics may improve initial tolerability",
            "Re-assess glycaemic targets every 3 months for the first year",
        ],
        "emerging_trends": [
            "Oral semaglutide 50 mg (PIONEER-PLUS) — superior to injectable liraglutide in head-to-head trial",
            "Tirzepatide (GIP+GLP-1): −2.4% HbA1c, −11.2 kg weight — SURPASS programme results",
            "Retatrutide (triple agonist GIP/GLP-1/glucagon): Phase 3 data expected Q3 2025",
            "GLP-1 RAs in non-alcoholic fatty liver disease: emerging hepatoprotective evidence",
        ],
        "evidence_quality": "High — supported by 34 RCTs, 3 Indian cohort studies, 2025 ADA/EASD guidelines. Recency: all sources within 24 months.",
        "short_article": (
            "RESEARCH UPDATE: GLP-1 Receptor Agonists — What's New in 2025\n\n"
            "A major 2025 meta-analysis of 87,420 patients reaffirms GLP-1 receptor agonists as the "
            "preferred add-on in Type 2 Diabetes with cardiovascular risk. Semaglutide continues to lead "
            "with a 1.8% HbA1c reduction and 6.2 kg weight loss at one year.\n\n"
            "KEY FINDING: For your Indian patients (BMI 23–27), GLP-1 RAs deliver a 1.6% HbA1c drop — "
            "comparable to Western data. Start at half dose to manage GI tolerability.\n\n"
            "WHY IT MATTERS: The 2025 ADA/EASD consensus now recommends GLP-1 RAs alongside metformin "
            "as first-line for any T2DM patient with established ASCVD, heart failure, or CKD.\n\n"
            "ACTION: Consider initiating semaglutide in your next eligible patient. Adherence counselling "
            "at week 4 reduces dropout by 40%.\n\n"
            "— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": ["GLP-1", "Semaglutide", "T2DM", "Cardiovascular", "HbA1c", "RCT", "Indian Population"],
        "sub_category": "Meta-Analysis / Systematic Review",
    },

    "SGLT2": {
        "title": "SGLT2 Inhibitors and Cardiovascular Outcomes in Heart Failure: EMPEROR and DAPA-HF 3-Year Follow-Up",
        "summary": (
            "Three-year follow-up data from EMPEROR-Reduced and DAPA-HF confirm SGLT2 inhibitors "
            "reduce hospitalisation for heart failure by 30% and CV mortality by 18% in both HFrEF "
            "and HFpEF patients, regardless of diabetes status. The 2025 ESC guidelines now give "
            "SGLT2 inhibitors a Class I, Level A recommendation for all HF patients."
        ),
        "key_findings": [
            "Empagliflozin reduces HF hospitalisation by 30% at 3 years (EMPEROR extended follow-up)",
            "Dapagliflozin effect consistent in HFpEF (EF >40%) — opens new treatment frontier",
            "SGLT2i benefit independent of baseline HbA1c or diabetes status",
            "eGFR decline slowed by 1.6 mL/min/year vs placebo — renal protection confirmed",
            "SGLT2i + GLP-1 RA combination: additive 44% reduction in MACE in T2DM+CVD cohort",
            "Indian HF registry data: SGLT2i reduces 30-day readmission by 27%",
        ],
        "clinical_insights": (
            "SGLT2 inhibitors are now standard of care for all heart failure patients — not just diabetics. "
            "The 2025 ESC HF guidelines give empagliflozin and dapagliflozin Class I recommendation "
            "irrespective of EF or diabetes. Key practice point: initiate in-hospital at HF admission "
            "for maximum benefit. Monitor for symptomatic hypotension and genital infections."
        ),
        "recommendations": [
            "Add SGLT2 inhibitor to all HFrEF patients on optimised GDMT regardless of diabetes",
            "Consider dapagliflozin for HFpEF — first evidence-based option in this population",
            "Initiate in-hospital at the time of HF admission when haemodynamically stable",
            "Monitor renal function at week 4; transient eGFR dip is expected and not a reason to stop",
            "Educate patients on genital hygiene to prevent mycotic infections",
        ],
        "emerging_trends": [
            "Sotagliflozin (SGLT1+2 dual inhibitor): Phase 3 SOLOIST data in acute HF",
            "SGLT2i in cardiac amyloidosis — exploratory signals in ATTR-HF patients",
            "Combination SGLT2i + sacubitril/valsartan: PARAGLIDE extension data",
        ],
        "evidence_quality": "High — Class I ESC 2025 guidelines, two landmark RCTs with 3-year follow-up, Indian registry data.",
        "short_article": (
            "RESEARCH UPDATE: SGLT2 Inhibitors — Now for ALL Heart Failure Patients\n\n"
            "The 3-year follow-up of EMPEROR-Reduced and DAPA-HF settles the debate: SGLT2 inhibitors "
            "reduce heart failure hospitalisation by 30% and cut CV mortality by 18% — regardless of "
            "whether the patient has diabetes.\n\n"
            "KEY FINDING: The 2025 ESC guidelines now give a Class I, Level A recommendation for SGLT2i "
            "in ALL HF patients — HFrEF and HFpEF alike.\n\n"
            "WHY IT MATTERS: Your HF patients without T2DM are missing a proven mortality benefit. "
            "Indian registry data shows a 27% reduction in 30-day readmissions.\n\n"
            "ACTION: Initiate empagliflozin or dapagliflozin in your next HF admission when the patient "
            "is haemodynamically stable.\n\n"
            "— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": ["SGLT2", "Heart Failure", "Empagliflozin", "Dapagliflozin", "HFrEF", "HFpEF", "ESC 2025"],
        "sub_category": "Clinical Trial / RCT",
    },

    "PCOS": {
        "title": "Inositol vs Metformin in PCOS: 2025 Systematic Review and Indian Cohort Data",
        "summary": (
            "A 2025 systematic review of 22 RCTs (n=3,180) demonstrates myo-inositol achieves "
            "comparable insulin sensitisation to metformin with significantly fewer GI adverse effects "
            "(12% vs 34%). Combined myo-inositol + d-chiro-inositol (40:1 ratio) shows superior "
            "menstrual regularity outcomes at 6 months. Indian data confirms efficacy across BMI ranges."
        ),
        "key_findings": [
            "Myo-inositol 4g/day: comparable HbA1c reduction to metformin 1500mg/day at 6 months",
            "GI adverse events: 12% (inositol) vs 34% (metformin) — p<0.001",
            "Menstrual regularity at 6 months: 78% (combined inositol) vs 64% (metformin)",
            "AMH levels improved by 23% with combined inositol vs 11% with metformin",
            "Indian cohort (n=420): inositol effective in lean PCOS (BMI <23) — metformin less effective",
            "Pregnancy rates at 12 months: 34% (inositol) vs 29% (metformin) in anovulatory PCOS",
        ],
        "clinical_insights": (
            "For Indian Gynaecologists: myo-inositol is now a strong alternative to metformin, "
            "particularly for lean PCOS patients (BMI <23) who are common in Indian practice and where "
            "metformin shows limited benefit. The 40:1 myo:d-chiro ratio is the evidence-based formulation. "
            "For patients seeking conception, inositol shows superior AMH response and pregnancy rates."
        ),
        "recommendations": [
            "First-line inositol (40:1 ratio, 4g/day) for lean PCOS or metformin-intolerant patients",
            "Combine with lifestyle intervention — synergistic benefit documented",
            "For obese PCOS with IR: metformin + inositol combination may offer best outcomes",
            "Monitor menstrual regularity at 3 months; assess AMH at 6 months",
            "For conception-seeking patients: prefer inositol as first-line over metformin",
        ],
        "emerging_trends": [
            "Inositol + NAC (N-acetylcysteine) combination: Phase 3 Indian trial ongoing",
            "Gut microbiome modulation as adjunct to inositol — early data promising",
            "Inositol in adolescent PCOS — safety and efficacy data emerging",
        ],
        "evidence_quality": "Moderate-High — 22 RCTs, Indian cohort data, 2025 ESHRE/ASRM position statement.",
        "short_article": (
            "RESEARCH UPDATE: Inositol Overtakes Metformin in PCOS?\n\n"
            "A 2025 meta-analysis of 3,180 PCOS patients finds myo-inositol matches metformin for "
            "insulin sensitisation — with only a 12% GI side effect rate vs 34% for metformin. "
            "Menstrual regularity improved in 78% of patients on combined inositol at 6 months.\n\n"
            "KEY FINDING: In Indian lean PCOS patients (BMI <23) — very common in your practice — "
            "metformin shows limited benefit while inositol delivers consistent results.\n\n"
            "WHY IT MATTERS: Your PCOS patients who struggle with metformin GI effects now have "
            "a well-evidenced, tolerable alternative with superior conception rates.\n\n"
            "ACTION: Consider switching metformin-intolerant PCOS patients to myo-inositol 4g/day "
            "(40:1 formulation).\n\n"
            "— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": ["PCOS", "Inositol", "Metformin", "Menstrual Regularity", "Fertility", "Indian Population"],
        "sub_category": "Meta-Analysis / Systematic Review",
    },
}

# Generic fallback template for any topic not in MOCK_LIBRARY
def _generic_content(topic: str, specialty: str, therapy_area: str) -> dict:
    return {
        "title": f"{topic}: 2025 Evidence Update and Clinical Practice Implications",
        "summary": (
            f"A comprehensive 2025 review consolidates the latest evidence on {topic}, drawing from "
            f"14 randomised controlled trials and 8 observational studies. The evidence supports a "
            f"paradigm shift in {specialty} practice with updated treatment algorithms relevant to "
            f"Indian patient populations."
        ),
        "key_findings": [
            f"Updated 2025 guidelines recommend earlier initiation of targeted therapy in {therapy_area}",
            f"Real-world data from Indian cohorts (n=1,840) confirms efficacy comparable to global trials",
            f"Combination approaches show 40% improvement in primary outcomes vs monotherapy",
            f"Safety profile consistent across diverse patient demographics including South Asian populations",
            f"Patient adherence significantly improved with simplified once-daily regimens",
            f"Cost-effectiveness analysis favours early intervention over watchful waiting strategy",
        ],
        "clinical_insights": (
            f"For {specialty} specialists: the 2025 evidence base firmly supports proactive management in "
            f"{therapy_area}. Key practice implications include earlier screening, targeted combination "
            f"therapy, and patient-centred shared decision making. Indian population-specific data now "
            f"available to guide dosing and monitoring protocols."
        ),
        "recommendations": [
            f"Screen high-risk patients for {therapy_area} at every encounter",
            f"Initiate evidence-based therapy without delay once diagnosis is confirmed",
            f"Follow 2025 updated guidelines for combination therapy selection",
            f"Monitor for treatment response at 3 and 6 months with validated tools",
            f"Educate patients on importance of adherence — adherence counselling improves outcomes by 35%",
        ],
        "emerging_trends": [
            f"Novel targeted agents in Phase 3 trials showing promise for {therapy_area}",
            f"Digital health tools improving monitoring and adherence in {specialty} practice",
            f"Personalised medicine approaches based on biomarker profiling gaining traction",
        ],
        "evidence_quality": "Moderate-High — 14 RCTs, 8 observational studies, 2025 society guidelines. Sources within 18 months.",
        "short_article": (
            f"RESEARCH UPDATE: {topic}\n\n"
            f"New 2025 evidence consolidates the treatment landscape in {therapy_area}. A multi-centre "
            f"review of 14 RCTs confirms that proactive, guideline-directed management delivers superior "
            f"patient outcomes with an acceptable safety profile across all patient groups.\n\n"
            f"KEY FINDING: Indian cohort data (n=1,840) confirms efficacy matching global trial results — "
            f"meaning the evidence is directly applicable to your patient population.\n\n"
            f"WHY IT MATTERS: Your {specialty.lower()} patients stand to benefit from updated "
            f"management approaches — combination strategies now show 40% better outcomes.\n\n"
            f"ACTION: Review your current {therapy_area} patients against 2025 guidelines at your next clinic.\n\n"
            f"— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": [topic.split()[0], specialty, therapy_area, "RCT", "Indian Population", "2025 Guidelines"],
        "sub_category": "Review Article",
    }


def run_mock_pipeline(topic: str, specialty: str, therapy_area: str,
                      run_store: dict, run_id: str) -> None:
    """
    Simulates the 4-agent pipeline with realistic delays.
    Updates run_store[run_id] at each step for live progress updates.
    """
    import time

    def update(agent: str, pct: int, msg: str):
        run_store[run_id].update({
            "current_agent": agent,
            "progress": pct,
            "status_msg": msg,
        })
        time.sleep(random.uniform(1.8, 2.8))  # simulate agent thinking time

    update("alpha", 10, "🔍 Agent Alpha: Searching PubMed and web sources...")
    update("alpha", 25, "📄 Agent Alpha: Reading relevant papers...")
    update("alpha", 40, "📝 Agent Alpha: Consolidating research article...")
    update("beta",  55, "🧠 Agent Beta: Extracting insights and key findings...")
    update("beta",  65, "📊 Agent Beta: Preparing clinical recommendations...")
    update("gamma", 75, "✍️  Agent Gamma: Writing doctor-friendly article...")
    update("gamma", 85, "📱 Agent Gamma: Formatting for WhatsApp & email delivery...")
    update("delta", 92, "🗂️  Agent Delta: Generating structured JSON report...")
    update("delta", 98, "✅ Agent Delta: Finalising for Pinnacle portal...")

    # Determine which mock content to use
    key = next((k for k in MOCK_LIBRARY if k.upper() in topic.upper()), None)
    content = MOCK_LIBRARY[key] if key else _generic_content(topic, specialty, therapy_area)

    run_store[run_id].update({
        "status": "completed",
        "progress": 100,
        "current_agent": "done",
        "status_msg": "Pipeline complete. Content ready for MA review.",
        "content": {
            "topic": topic,
            "specialty": specialty,
            "therapy_area": therapy_area,
            **content,
        },
    })
