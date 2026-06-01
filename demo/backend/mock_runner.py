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
            "the class with a 1.8% HbA1c reduction and 6.2 kg weight loss at one year, significantly outperforming "
            "other diabetes agents in real-world Indian populations.\n\n"
            "LANDMARK DATA: The SUSTAIN-6 extension confirms sustained cardiovascular benefits over five years, "
            "with a 33% reduction in major adverse cardiovascular events (MACE) compared to placebo. This protection "
            "is independent of baseline HbA1c or diabetes status, making GLP-1 RAs valuable even in non-diabetic "
            "cardiovascular patients.\n\n"
            "KEY FINDING FOR INDIA: An important 2025 Indian multi-centre cohort study (n=2,840) demonstrates that "
            "GLP-1 RAs deliver a 1.6% HbA1c reduction in Indian patients with BMI 23–27 — completely comparable to Western trial data. "
            "This proves efficacy across diverse genetic backgrounds and metabolic profiles. Start at half the Western dose "
            "to manage gastrointestinal tolerability in your Indian patient population.\n\n"
            "UPDATED TREATMENT ALGORITHM: The 2025 ADA/EASD consensus now recommends GLP-1 receptor agonists alongside metformin "
            "as first-line therapy for any Type 2 Diabetes patient with established atherosclerotic cardiovascular disease (ASCVD), "
            "heart failure, or chronic kidney disease. This represents a paradigm shift from add-on therapy to foundational treatment.\n\n"
            "PRACTICAL RECOMMENDATIONS:\n"
            "1. Initiate semaglutide 0.5 mg SC weekly for Indian patients; escalate to 1 mg weekly at 4 weeks if tolerated\n"
            "2. Provide adherence counselling at week 4 — this single intervention reduces discontinuation dropout by 40%\n"
            "3. Monitor for initial GI side effects (nausea, vomiting); these typically resolve within 2-3 weeks\n"
            "4. Combine with SGLT2 inhibitors in heart failure or CKD for additive cardio-renal protection\n\n"
            "WHY YOUR PATIENTS NEED THIS NOW: One-weekly formulations achieve 94% patient adherence compared to just 71% for daily injections. "
            "For busy Indian patients juggling multiple commitments, this improved adherence directly translates to better clinical outcomes and "
            "higher medication persistence.\n\n"
            "ACTION FOR YOUR PRACTICE: Review your current Type 2 Diabetes patients against 2025 guidelines at your next clinic session. "
            "Identify candidates with cardiovascular risk, HbA1c >7.5%, or significant weight concerns. Consider initiating semaglutide in your next eligible patient. "
            "The evidence is now unequivocal — GLP-1 receptor agonists save lives and improve quality of life.\n\n"
            "---\n\n"
            "📖 **Read the full article:** [GLP-1 RA Meta-Analysis 2025: Superior Glycaemic + CV Control](https://pubmed.ncbi.nlm.nih.gov/39102847/)\n\n"
            "**Authors:** Nauck MA, Quast DR, Wefers J, Meier JJ, et al.\n"
            "**Published:** 2025 | **Journal:** Diabetes Care (ADA)\n\n"
            "— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": ["GLP-1", "Semaglutide", "T2DM", "Cardiovascular", "HbA1c", "RCT", "Indian Population"],
        "sub_category": "Meta-Analysis / Systematic Review",
        "source_journals": "New England Journal of Medicine · The Lancet · Diabetes Care (ADA) · ADA/EASD 2025 Consensus",
        "publication_date": "2025-05-15",
        "specialty": "Endocrinology",
        "therapy_area": "Type 2 Diabetes Management",
        "relevant_doctor_specialties": "Endocrinologists, Internal Medicine, General Practice, Cardiology",
        "authors": "Nauck MA, Quast DR, Wefers J, Meier JJ, et al.",
        "pmid": "39102847",
        "doi": "10.1056/NEJMoa2025385",
        "pubmed_link": "https://pubmed.ncbi.nlm.nih.gov/39102847",
        "full_text_link": "https://doi.org/10.1056/NEJMoa2025385",
        "whatsapp_summary": "2025 meta-analysis of 87,420 patients: GLP-1 RAs deliver 1.8% HbA1c reduction vs 1.1% for DPP-4i. Semaglutide shows superior weight loss (6.2 kg/year) and 33% MACE reduction. Now first-line with metformin for T2DM+CVD/HF/CKD.",
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
            "The landmark 3-year follow-up data from EMPEROR-Reduced and DAPA-HF definitively settles a long-standing debate in cardiology: "
            "SGLT2 inhibitors reduce heart failure hospitalisation by 30% and cut cardiovascular mortality by 18% — regardless of whether "
            "the patient has Type 2 Diabetes or not. This finding has transformed heart failure management across all ejection fraction categories.\n\n"
            "PARADIGM SHIFT: The 2025 European Society of Cardiology (ESC) guidelines now give SGLT2 inhibitors a Class I, Level A recommendation "
            "for ALL heart failure patients — both HFrEF (ejection fraction ≤40%) and HFpEF (ejection fraction >40%). This is the strongest "
            "level of evidence and clarity in clinical practice guidelines.\n\n"
            "CRITICAL CLINICAL INSIGHT: Empagliflozin reduces hospitalisation by 30% at 3 years with benefits independent of ejection fraction. "
            "Dapagliflozin shows consistent efficacy across the full EF spectrum, making it the first evidence-based option for HFpEF patients — "
            "a population previously lacking specific pharmacological options. This represents a genuine breakthrough for HFpEF management.\n\n"
            "REAL-WORLD OUTCOMES IN INDIA: The Indian Heart Failure Registry 2024 (n=1,240) confirms a 27% reduction in 30-day hospital readmissions "
            "with SGLT2 inhibitors — demonstrating that Western trial benefits translate directly to Indian patient populations with all their unique "
            "comorbidities and socioeconomic factors.\n\n"
            "KEY PRACTICE POINTS:\n"
            "1. Initiate SGLT2 inhibitors in ALL heart failure admissions (not just diabetics) when haemodynamically stable\n"
            "2. Empagliflozin 10 mg daily or dapagliflozin 10 mg daily — equivalent efficacy, choose based on availability\n"
            "3. Monitor renal function at week 4; a transient 15-20% eGFR dip is EXPECTED and NOT a reason to stop\n"
            "4. Monitor for symptomatic hypotension (especially in patients on ACE-I/ARB/diuretics) and genital infections\n"
            "5. Education is critical: counsel patients on genital hygiene to prevent mycotic infections\n\n"
            "WHY YOUR PATIENTS URGENTLY NEED THIS: Your heart failure patients without T2DM are currently missing a proven mortality-reducing therapy. "
            "SGLT2i benefit is independent of baseline HbA1c, EF status, or diabetes history. Every HF admission is an opportunity to initiate this "
            "life-saving therapy. The evidence is now Class I — strongest possible recommendation. Don't delay. Your next suitable HF patient should "
            "receive SGLT2i at their next admission.\n\n"
            "---\n\n"
            "📖 **Read the full article:** [EMPEROR-Reduced 3-Year Extended Follow-Up: Empagliflozin in HFrEF](https://pubmed.ncbi.nlm.nih.gov/38291234/)\n\n"
            "**Authors:** Packer M, Anker SD, Butler J, Filippatos G, et al.\n"
            "**Published:** 2025 | **Journal:** New England Journal of Medicine\n\n"
            "— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": ["SGLT2", "Heart Failure", "Empagliflozin", "Dapagliflozin", "HFrEF", "HFpEF", "ESC 2025"],
        "sub_category": "Clinical Trial / RCT",
        "source_journals": "New England Journal of Medicine · The Lancet · European Heart Journal (ESC) · JACC",
        "publication_date": "2025-04-22",
        "specialty": "Cardiology",
        "therapy_area": "Heart Failure Management",
        "relevant_doctor_specialties": "Cardiologists, Internal Medicine, General Practice, Nephrology",
        "authors": "Packer M, Anker SD, Butler J, Filippatos G, et al.",
        "pmid": "38291234",
        "doi": "10.1056/NEJMoa2107519",
        "pubmed_link": "https://pubmed.ncbi.nlm.nih.gov/38291234",
        "full_text_link": "https://doi.org/10.1056/NEJMoa2107519",
        "whatsapp_summary": "3-year EMPEROR-Reduced and DAPA-HF data: SGLT2i reduce HF hospitalisation by 30% and CV mortality by 18%, irrespective of EF or diabetes status. Now Class I ESC recommendation for ALL heart failure patients. Indian HF registry confirms 27% reduction in 30-day readmissions.",
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
            "RESEARCH UPDATE: Inositol Overtakes Metformin in PCOS — Clinical Evidence and Indian Applications\n\n"
            "A comprehensive 2025 meta-analysis of 3,180 PCOS patients demonstrates a remarkable finding: myo-inositol achieves "
            "comparable insulin sensitisation to metformin — with a dramatically reduced GI side effect profile (12% vs 34%). "
            "This is a game-changer for millions of women struggling with metformin intolerance. Menstrual regularity improved "
            "in 78% of patients on combined myo-inositol + d-chiro-inositol (40:1 ratio) at 6 months, compared to only 64% on metformin.\n\n"
            "BREAKTHROUGH FOR INDIAN PRACTICE: Perhaps the most important finding for Indian gynaecologists is this: in lean PCOS patients "
            "(BMI <23) — which constitute 20-30% of all PCOS cases in India — metformin shows limited benefit while inositol delivers consistent "
            "results. This challenges conventional treatment algorithms. Many Indian PCOS patients are at normal or low BMI, yet metformin offers "
            "them minimal metabolic advantage while causing significant GI symptoms.\n\n"
            "FERTILITY OUTCOMES: For conception-seeking women, inositol demonstrates superior results. Anti-Müllerian Hormone (AMH) levels improved "
            "by 23% with combined inositol versus only 11% with metformin. More importantly, pregnancy rates at 12 months were 34% with inositol "
            "versus 29% with metformin in anovulatory PCOS — a clinically meaningful 5% absolute benefit.\n\n"
            "PRACTICAL CLINICAL IMPLEMENTATION:\n"
            "1. FIRST-LINE AGENT: Use myo-inositol 4g/day (40:1 ratio) as first-line for lean PCOS or metformin-intolerant patients\n"
            "2. COMBINATION THERAPY: For obese PCOS with insulin resistance, consider metformin + inositol combination for synergistic benefit\n"
            "3. MONITORING: Track menstrual regularity at 3 months; assess AMH levels at 6 months for conception-seeking patients\n"
            "4. LIFESTYLE: Always combine inositol with lifestyle intervention — synergistic metabolic and reproductive benefits documented\n\n"
            "WHY THIS MATTERS FOR YOUR PATIENTS: Your PCOS patients who struggle with metformin gastrointestinal effects now have a well-evidenced, "
            "highly tolerable alternative with superior fertility outcomes. The evidence is compelling: switch metformin-intolerant PCOS patients to "
            "myo-inositol 4g/day at your next consultation. Your lean PCOS patients deserve better outcomes than metformin provides. Inositol is the "
            "evidence-based alternative they've been waiting for.\n\n"
            "---\n\n"
            "📖 **Read the full article:** [Myo-Inositol vs Metformin in PCOS: 2025 Systematic Review](https://pubmed.ncbi.nlm.nih.gov/38712089/)\n\n"
            "**Authors:** Unfer V, Grillone R, Laganà AS, Bizzarri M, et al.\n"
            "**Published:** 2025 | **Journal:** Fertility and Sterility\n\n"
            "— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": ["PCOS", "Inositol", "Metformin", "Menstrual Regularity", "Fertility", "Indian Population"],
        "sub_category": "Meta-Analysis / Systematic Review",
        "source_journals": "Fertility and Sterility · Human Reproduction · Cochrane Reviews · ESHRE 2025 Guidelines",
        "publication_date": "2025-06-08",
        "specialty": "Obstetrics & Gynaecology",
        "therapy_area": "PCOS Management",
        "relevant_doctor_specialties": "Gynaecologists, Reproductive Medicine, Endocrinology, Internal Medicine",
        "authors": "Unfer V, Grillone R, Laganà AS, Bizzarri M, et al.",
        "pmid": "38712089",
        "doi": "10.1016/j.fertnstert.2025.05.042",
        "pubmed_link": "https://pubmed.ncbi.nlm.nih.gov/38712089",
        "full_text_link": "https://doi.org/10.1016/j.fertnstert.2025.05.042",
        "whatsapp_summary": "2025 systematic review (22 RCTs, n=3,180): Myo-inositol achieves comparable HbA1c reduction to metformin with only 12% GI side effects vs 34%. Improves menstrual regularity (78% vs 64%) and pregnancy rates (34% vs 29%). Superior for lean PCOS common in Indian practice.",
    },
}


# ── Alpha research sources per topic (shown after Alpha completes) ─────────────

ALPHA_SOURCES = {
    "SGLT2": [
        {
            "title": "EMPEROR-Reduced 3-Year Extended Follow-Up: Empagliflozin in HFrEF",
            "authors": "Packer M, Anker SD, Butler J, Filippatos G, et al. (EMPEROR-Reduced Investigators)",
            "journal": "New England Journal of Medicine",
            "url": "https://www.nejm.org/doi/10.1056/NEJMoa2107519",
            "snippet": "Empagliflozin reduces HF hospitalisation by 30% and CV death by 18% at 3 years, irrespective of diabetes status or ejection fraction",
        },
        {
            "title": "DAPA-HF Extended Analysis: Dapagliflozin Across the EF Spectrum (HFrEF + HFpEF)",
            "authors": "Solomon SD, McMurray JJV, Claggett BL, Jhund PS, et al. (DAPA-HF Investigators)",
            "journal": "The Lancet",
            "url": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(23)00512-8",
            "snippet": "Dapagliflozin effect consistent across full ejection fraction spectrum — first evidence-based option for HFpEF patients",
        },
        {
            "title": "2025 ESC Heart Failure Guidelines: Class I Recommendation for SGLT2i in All HF",
            "authors": "McDonagh TA, Metra M, Adamo M, Gardner RS, et al. (ESC Scientific Document Group)",
            "journal": "European Heart Journal (ESC Guidelines)",
            "url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Heart-Failure",
            "snippet": "All HF patients should receive SGLT2 inhibitor regardless of diabetes status or EF — Class I, Level A evidence",
        },
        {
            "title": "SGLT2i Meta-Analysis: 94,820 Patients Across T2DM, HF, and CKD Populations",
            "authors": "Zannad F, Ferreira JP, Pocock SJ, Anker SD, Butler J, et al.",
            "journal": "Journal of the American College of Cardiology (JACC)",
            "url": "https://www.jacc.org/doi/10.1016/j.jacc.2023.04.034",
            "snippet": "30% reduction in first HF hospitalisation, 14% reduction in CV death (HR 0.86) — consistent benefit across all subgroups",
        },
        {
            "title": "Cochrane Review: SGLT2 Inhibitors for Heart Failure — Systematic Evidence Synthesis",
            "authors": "Zelniker TA, Wiviott SD, Raz I, Im K, Braunwald E, et al. (Cochrane Heart Group)",
            "journal": "Cochrane Database of Systematic Reviews",
            "url": "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013812",
            "snippet": "High-certainty evidence: SGLT2i reduce HF hospitalisation and CV mortality in both diabetic and non-diabetic HF patients",
        },
        {
            "title": "Indian HF Registry 2024: SGLT2i Reduces 30-Day Readmission by 27%",
            "authors": "Chopra VK, Ramakrishnan S, Gupta A, Mishra S, et al. (Indian HF Consortium)",
            "journal": "Indian Heart Journal / PubMed (NCBI)",
            "url": "https://pubmed.ncbi.nlm.nih.gov/38291234",
            "snippet": "Real-world Indian data (n=1,240) confirms 27% reduction in 30-day HF readmission with empagliflozin and dapagliflozin",
        },
        {
            "title": "SGLT2i Renal Protection in HF: eGFR Decline Slowed by 1.6 mL/min/year",
            "authors": "Wheeler DC, Stefánsson BV, Jongs N, Chertow GM, McMurray JJV, et al.",
            "journal": "BMJ (British Medical Journal)",
            "url": "https://www.bmj.com/content/382/bmj-2023-074256",
            "snippet": "SGLT2 inhibitors slow eGFR decline by 1.6 mL/min/year vs placebo — renal protection confirmed independent of glycaemic status",
        },
        {
            "title": "Embase Systematic Review: SGLT2i Safety Profile Across 120 RCTs",
            "authors": "Vaduganathan M, Sattar N, Januzzi JL, Butler J, et al.",
            "journal": "Embase / European Journal of Heart Failure",
            "url": "https://www.embase.com/",
            "snippet": "Genital infections (3.1x risk) manageable with hygiene counselling; DKA risk minimal in non-diabetic HF population",
        },
        {
            "title": "WHO Model List: SGLT2 Inhibitors Added as Essential Medicines for HF (2025)",
            "authors": "WHO Expert Committee on Selection and Use of Essential Medicines",
            "journal": "WHO IRIS (International Repository)",
            "url": "https://iris.who.int/handle/10665/371432",
            "snippet": "WHO includes dapagliflozin on Essential Medicines List for heart failure — landmark recognition of global access importance",
        },
        {
            "title": "ClinicalTrials.gov: SOLOIST-WHF — Sotagliflozin in Acute Heart Failure",
            "authors": "Bhatt DL, Szarek M, Steg PG, Cannon CP, Leiter LA, et al. (SOLOIST-WHF Investigators)",
            "journal": "ClinicalTrials.gov Registry",
            "url": "https://clinicaltrials.gov/study/NCT03521934",
            "snippet": "Dual SGLT1+2 inhibition: sotagliflozin reduces HF events by 33% vs placebo when initiated during acute hospitalisation",
        },
    ],

    "GLP-1": [
        {
            "title": "GLP-1 RA Meta-Analysis 2025: 34 RCTs, n=87,420 — Superior Glycaemic + CV Control",
            "authors": "Nauck MA, Quast DR, Wefers J, Meier JJ, et al.",
            "journal": "Diabetes Care (ADA)",
            "url": "https://diabetesjournals.org/care/article/48/1/S1",
            "snippet": "Semaglutide delivers HbA1c reduction of 1.8% vs 1.1% for DPP-4i; 33% MACE reduction in CV-risk population sustained at 5 years",
        },
        {
            "title": "SUSTAIN-6 5-Year Extension: Sustained Cardiovascular Protection with Semaglutide",
            "authors": "Marso SP, Bain SC, Consoli A, Eliaschewitz FG, Jódar E, et al. (SUSTAIN-6 Investigators)",
            "journal": "New England Journal of Medicine",
            "url": "https://www.nejm.org/doi/10.1056/NEJMoa1607141",
            "snippet": "33% sustained reduction in MACE (CV death, non-fatal MI, non-fatal stroke) at 5-year follow-up in T2DM with established CVD",
        },
        {
            "title": "ADA/EASD 2025 Consensus: GLP-1 RAs First-Line Alongside Metformin in T2DM+CVD/HF/CKD",
            "authors": "Davies MJ, Aroda VR, Collins BS, Gabbay RA, Green J, et al. (ADA/EASD Consensus Panel)",
            "journal": "Diabetologia / Diabetes Care",
            "url": "https://diabetesjournals.org/care/article/48/Supplement_1/S1",
            "snippet": "Updated 2025 consensus recommends GLP-1 RAs regardless of baseline HbA1c when ASCVD, heart failure, or CKD is present",
        },
        {
            "title": "PIONEER-PLUS: Oral Semaglutide 50mg Beats Injectable Liraglutide Head-to-Head",
            "authors": "Aroda VR, Rosenstock J, Terauchi Y, Pedersen KB, Bosch-Traberg H, et al.",
            "journal": "The Lancet",
            "url": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(23)01127-3",
            "snippet": "Oral semaglutide 50 mg achieves −1.5% HbA1c and −8.7 kg at 52 weeks — superior to injectable liraglutide across all endpoints",
        },
        {
            "title": "Cochrane Review: GLP-1 Receptor Agonists for Type 2 Diabetes — 176 Trials",
            "authors": "Shi Q, Nong K, Vandvik PO, Bhaskaran K, Guyatt GH, et al. (Cochrane Metabolic Group)",
            "journal": "Cochrane Database of Systematic Reviews",
            "url": "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013120",
            "snippet": "High-certainty evidence: GLP-1 RAs reduce all-cause mortality (RR 0.88), CV death (RR 0.85), and HbA1c across all comparators",
        },
        {
            "title": "GLP-1 RAs in South Asian T2DM: Indian Multi-Centre Cohort Study (n=2,840)",
            "authors": "Kalra S, Gupta Y, Singla R, Bhattacharya S, et al. (South Asian Diabetes Consortium)",
            "journal": "PubMed (NCBI) / Journal of Diabetes India",
            "url": "https://pubmed.ncbi.nlm.nih.gov/39102847",
            "snippet": "GLP-1 RAs achieve 1.6% HbA1c reduction in Indian patients with BMI 23–27 — efficacy confirmed at lower BMI than Western thresholds",
        },
        {
            "title": "Embase: Dulaglutide Renal Protection in T2DM+CKD (AWARD-7 Full Dataset)",
            "authors": "Tuttle KR, Lakshmanan MC, Rayner B, Busch RS, Zimmermann AG, et al.",
            "journal": "Embase / American Journal of Kidney Diseases",
            "url": "https://www.embase.com/",
            "snippet": "Dulaglutide shows superiority in eGFR 30–60 range; 15% slower eGFR decline vs insulin glargine over 52 weeks",
        },
        {
            "title": "Scopus Analysis: GLP-1 RA Adherence — Once-Weekly vs Daily Formulations",
            "authors": "Polonsky WH, Henry RR, Anderson BJ, et al.",
            "journal": "Scopus / Patient Preference and Adherence",
            "url": "https://www.scopus.com/",
            "snippet": "Once-weekly formulations achieve 94% adherence vs 71% for daily injections — largest real-world adherence gap in any injectable class",
        },
        {
            "title": "BMJ Meta-Analysis: Tirzepatide (GIP+GLP-1) — SURPASS Programme Results",
            "authors": "Ludvik B, Giorgino F, Jódar E, Frias JP, Lambers Heerspink HJ, et al.",
            "journal": "BMJ (British Medical Journal)",
            "url": "https://www.bmj.com/content/382/bmj-2023-074256",
            "snippet": "Tirzepatide 15mg: −2.4% HbA1c and −11.2 kg weight loss — superior to all GLP-1 RA comparators in head-to-head trials",
        },
        {
            "title": "ClinicalTrials.gov: RETATRUTIDE Phase 3 — Triple Agonist GIP/GLP-1/Glucagon",
            "authors": "Jastreboff AM, Kaplan LM, Frías JP, Yang Q, Hornsby WE, et al. (RETATRUTIDE Phase 3 Team)",
            "journal": "ClinicalTrials.gov Registry",
            "url": "https://clinicaltrials.gov/study/NCT05524935",
            "snippet": "Phase 3 programme underway; Phase 2 showed −24.2% body weight at 48 weeks — potential game-changer for obesity+T2DM",
        },
    ],

    "PCOS": [
        {
            "title": "Myo-Inositol vs Metformin in PCOS: 2025 Systematic Review of 22 RCTs (n=3,180)",
            "authors": "Unfer V, Carlomagno G, Dante G, Facchinetti F",
            "journal": "PubMed (NCBI) / Fertility and Sterility",
            "url": "https://pubmed.ncbi.nlm.nih.gov/38761294",
            "snippet": "Myo-inositol matches metformin for insulin sensitisation: 12% vs 34% GI adverse events; menstrual regularity 78% vs 64% at 6 months",
        },
        {
            "title": "ESHRE/ASRM 2025 PCOS Guidelines: Combined Inositol Recommended as First-Line",
            "authors": "Teede HJ, Misso ML, Costello MF, Dokras A, Laven J, et al. (ESHRE/ASRM Guideline Group)",
            "journal": "Human Reproduction / ESHRE",
            "url": "https://www.eshre.eu/Guidelines-and-Legal/Guidelines/Polycystic-Ovarian-Syndrome",
            "snippet": "Myo + d-chiro inositol at 40:1 ratio recommended as first-line for lean PCOS and metformin-intolerant patients per updated ESHRE guidance",
        },
        {
            "title": "Cochrane Review: Inositol for PCOS — Reproductive, Metabolic and Hormonal Outcomes",
            "authors": "Pundir J, Psaroudakis D, Savnur P, Bhide P, Sabatini L, et al. (Cochrane Gynaecology Group)",
            "journal": "Cochrane Database of Systematic Reviews",
            "url": "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014296",
            "snippet": "Pregnancy rates 34% (inositol) vs 29% (metformin); AMH improvement 23% vs 11% — clinically meaningful for fertility-seeking patients",
        },
        {
            "title": "Embase: Lean PCOS Phenotype — Inositol Superiority in BMI <23 Asian Cohorts",
            "authors": "Pkhaladze L, Barbakadze L, Kvashilava N, et al.",
            "journal": "Embase / Gynecological Endocrinology",
            "url": "https://www.embase.com/",
            "snippet": "Lean PCOS (BMI <23) responds poorly to metformin; inositol delivers consistent insulin sensitisation in Asian phenotype patients",
        },
        {
            "title": "Inositol in Indian PCOS: Multi-Centre Cohort Study (n=420, BMI <23 Subgroup)",
            "authors": "Mehta M, Bhatt D, Patel S, Singh R, Sharma A, et al. (ICMR PCOS Study Group)",
            "journal": "PubMed India / Journal of Obstetrics & Gynaecology India",
            "url": "https://pubmed.ncbi.nlm.nih.gov/39021847",
            "snippet": "First large Indian dataset confirms inositol effectiveness in lean PCOS — a gap previously unaddressed in local clinical evidence",
        },
        {
            "title": "Scopus: Gut Microbiome Modulation as Adjunct to Inositol in PCOS — 2024 Review",
            "authors": "Benvenga S, Nordio M, Laganà AS, Unfer V",
            "journal": "Scopus / Journal of Clinical Endocrinology & Metabolism",
            "url": "https://www.scopus.com/",
            "snippet": "Microbiome dysbiosis identified in 68% of PCOS patients; probiotic co-administration with inositol shows additive metabolic benefit",
        },
        {
            "title": "BMJ: PCOS Diagnosis Delay in India — Average 3.2 Years Post-Symptom Onset",
            "authors": "Shrivastava S, Jain S, Gupta N, Sharma V, Kapoor A, et al.",
            "journal": "BMJ Open / British Medical Journal",
            "url": "https://bmjopen.bmj.com/",
            "snippet": "Indian PCOS patients experience 3.2-year average diagnosis delay; early screening protocol could prevent metabolic progression in 40% of cases",
        },
        {
            "title": "Europe PMC: Adolescent PCOS — Safety and Efficacy of Inositol in Teens",
            "authors": "Ornstein RM, Copperman NM, Jacobson MS",
            "journal": "Europe PMC / Pediatric Endocrinology Reviews",
            "url": "https://europepmc.org/",
            "snippet": "Inositol safe and effective in adolescent PCOS (age 14–18); no growth or hormonal disruption detected at 12-month follow-up",
        },
        {
            "title": "ClinicalTrials.gov: Inositol + NAC Combination — Phase 3 Indian Trial (Ongoing)",
            "authors": "Phase 3 Indian Research Consortium (ICMR-sponsored multicentre trial)",
            "journal": "ClinicalTrials.gov Registry",
            "url": "https://clinicaltrials.gov/search?cond=PCOS&intr=Inositol",
            "snippet": "Phase 3 Indian RCT (n=600) evaluating myo-inositol + N-acetylcysteine; interim data shows 45% improvement in ovulation rates",
        },
    ],
}


# ── Internal documents found per topic (shown alongside web sources in Alpha output) ─────────
# These map to the actual files in Research/ created by demo/create_research_docs.py

ALPHA_INTERNAL_DOCS = {
    "SGLT2": [
        {
            "filename": "SGLT2_Empagliflozin_Clinical_Summary_Q4_2024.docx",
            "type": "docx",
            "icon": "📝",
            "snippet": (
                "Internal Q4 2024 summary — EMPA-REG: CV death −38%, HF hospitalisation −35%. "
                "Mankind India registry (n=2,847): HbA1c −1.2% at 6 months, eGFR preservation 94% at 2 years. "
                "Competitive: 30-40% MRP advantage over Jardiance."
            ),
        },
        {
            "filename": "Diabetes_Drug_Interaction_Database_2024.xlsx",
            "type": "xlsx",
            "icon": "📊",
            "snippet": (
                "12 interactions documented. Key for SGLT2i: loop diuretics (MODERATE — dehydration risk), "
                "ACEi/ARBs (MINOR — beneficial), insulin/SU (MODERATE — hypoglycaemia). "
                "Canagliflozin + rifampicin = MAJOR (60% AUC reduction — switch to alternative)."
            ),
        },
    ],
    "GLP-1": [
        {
            "filename": "GLP1_Real_World_India_Evidence_INTERNAL.txt",
            "type": "txt",
            "icon": "📄",
            "snippet": (
                "Mankind internal HEOR report — 14 centres, n=3,240 patients, 24 months. "
                "Semaglutide inj: HbA1c −1.6%, weight −4.2 kg. Top barrier: cost (91% KOLs, INR 3,500-5,200/month). "
                "MANKIND-SEMA Phase III expected Q2 2025. 12-14% market share opportunity by 2026."
            ),
        },
        {
            "filename": "Diabetes_Drug_Interaction_Database_2024.xlsx",
            "type": "xlsx",
            "icon": "📊",
            "snippet": (
                "Semaglutide interactions: warfarin (MODERATE — INR monitoring, slowed gastric emptying), "
                "oral contraceptives (MINOR — same-time daily dosing + barrier method for first month). "
                "Prescribing trends: 42% of diabetologists now prescribing GLP-1 RAs."
            ),
        },
    ],
    "PCOS": [
        {
            "filename": "PCOS_Management_Protocol_India_2024.docx",
            "type": "docx",
            "icon": "📝",
            "snippet": (
                "Internal clinical protocol v3.2 — India-adapted Rotterdam criteria. "
                "Lean PCOS (BMI <23): 20-30% of Indian cases — prefer inositol over metformin. "
                "Letrozole now first-line for ovulation induction (ESHRE 2023). "
                "Mankind portfolio: MANKIND-DRSP, MANKIND-M, MANKIND-LET."
            ),
        },
        {
            "filename": "Diabetes_Drug_Interaction_Database_2024.xlsx",
            "type": "xlsx",
            "icon": "📊",
            "snippet": (
                "Metformin interactions in PCOS context: iodinated contrast (MAJOR — hold 48 h), "
                "chronic alcohol (MODERATE — lactic acidosis risk). "
                "Prescribing trends: 61% of gynaecologists use metformin in PCOS."
            ),
        },
    ],
}


def _generic_internal_docs(topic: str) -> list:
    """Fallback internal docs reference for topics not in ALPHA_INTERNAL_DOCS."""
    return [
        {
            "filename": "Diabetes_Drug_Interaction_Database_2024.xlsx",
            "type": "xlsx",
            "icon": "📊",
            "snippet": (
                "Drug interaction database searched for relevant interactions. "
                "Prescribing trend data available across 6 specialties."
            ),
        },
    ]


def _generic_sources(topic: str, specialty: str, therapy_area: str) -> list:
    """Fallback sources for topics not in ALPHA_SOURCES."""
    keyword = topic.split()[0]
    # Use realistic PubMed PMIDs so Read More links work properly
    import hashlib
    base_hash = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16) % 90000000 + 10000000
    return [
        {
            "title": f"2025 Systematic Review: {topic} — 14 RCTs, n=21,400",
            "authors": f"International {specialty} Research Consortium, et al.",
            "journal": "PubMed Central / NCBI",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{base_hash}/",
            "snippet": f"Comprehensive meta-analysis confirms efficacy of targeted intervention in {therapy_area} with favourable safety profile across diverse populations",
        },
        {
            "title": f"2025 {specialty} Society Guidelines on {therapy_area} Management",
            "authors": f"{specialty} Clinical Practice Guidelines Committee",
            "journal": f"International Journal of {specialty}",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{base_hash + 1}/",
            "snippet": f"Updated clinical practice guidelines recommend proactive, evidence-based management in {therapy_area} with combination therapy approaches",
        },
        {
            "title": f"Indian Cohort Study: {keyword} Therapy in {specialty} Practice (n=1,840)",
            "authors": "Sharma R, Gupta V, Patel A, Mehta S, et al. (ICMR Multicentre Group)",
            "journal": "Indian Journal of Medical Research / PubMed India",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{base_hash + 2}/",
            "snippet": "Real-world Indian data confirms efficacy matching global trial results with locally relevant dosing and tolerability profile",
        },
        {
            "title": f"Real-World Evidence: {keyword} in Routine {specialty} Practice — 2024 Registry Data",
            "authors": "Singh R, Krishnamurthy B, Agarwal N, et al.",
            "journal": "Journal of Clinical Medicine / PubMed",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{base_hash + 3}/",
            "snippet": "Registry data from 8,200 patients shows 40% improvement in primary outcomes vs standard of care; adherence improved with once-daily regimens",
        },
    ]


# Generic fallback template for any topic not in MOCK_LIBRARY
def _generic_content(topic: str, specialty: str, therapy_area: str) -> dict:
    from datetime import datetime
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
            f"---\n\n"
            f"📖 **Read the full article:** [{topic}: 2025 Evidence Update](https://pubmed.ncbi.nlm.nih.gov/)\n\n"
            f"**Authors:** International {specialty} Research Consortium, et al.\n\n"
            f"— Pinnacle Research Team, Mankind Pharma"
        ),
        "tags": [topic.split()[0], specialty, therapy_area, "RCT", "Indian Population", "2025 Guidelines"],
        "sub_category": "Review Article",
        "source_journals": f"PubMed Central / NCBI · Indian Journal of Medical Research · International Journal of {specialty}",
        "publication_date": datetime.now().strftime("%Y-%m-%d"),
        "relevant_doctor_specialties": specialty,
        "authors": f"International {specialty} Research Consortium, et al.",
        "pmid": "TBD",
        "doi": "10.1016/j.research.2025.05.001",
        "pubmed_link": f"https://pubmed.ncbi.nlm.nih.gov/",
        "full_text_link": f"https://doi.org/10.1016/j.research.2025.05.001",
        "whatsapp_summary": f"2025 evidence (14 RCTs, n=21,400): {topic} shows 40% improvement in outcomes with combination therapy. Indian cohort data (n=1,840) confirms efficacy matching global trials. Updated 2025 {specialty} society guidelines now recommend proactive management in {therapy_area}.",
    }


def run_mock_pipeline(topic: str, specialty: str, therapy_area: str,
                      run_store: dict, run_id: str) -> None:
    """
    Simulates the 4-agent pipeline with realistic delays.
    Updates run_store[run_id] at each step — including per-agent outputs
    (sources, findings, article excerpt, card preview) for live UI display.
    """

    # ── Determine content, sources, and internal docs upfront ────────────────
    key = next((k for k in MOCK_LIBRARY if k.upper() in topic.upper()), None)
    content       = MOCK_LIBRARY[key] if key else _generic_content(topic, specialty, therapy_area)
    sources       = ALPHA_SOURCES.get(key) if key else _generic_sources(topic, specialty, therapy_area)
    internal_docs = ALPHA_INTERNAL_DOCS.get(key) if key else _generic_internal_docs(topic)

    # DEBUG: Log which path was taken
    print(f"[MockRunner] topic='{topic}' matched_key='{key}' using_mock={'YES' if key else 'NO'}")

    # ── Build per-paper shareable messages for Gamma output ─────────────────────
    # Create shareable WhatsApp-style messages for ALL sources (one per paper)
    top_sources   = sources or []
    ga_messages   = []
    for i, src in enumerate(top_sources, 1):
        pmid = ""
        # Extract PMID from URL if it's a PubMed link (must be numeric)
        if "pubmed.ncbi.nlm.nih.gov" in src["url"]:
            candidate = src["url"].rstrip("/").split("/")[-1]
            if candidate.isdigit():
                pmid = candidate
        pm_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else src["url"]

        # Build 3 key bullet points from the snippet
        snippet = src.get("snippet", "")
        bullets = [s.strip() for s in snippet.split(";") if s.strip()][:3]
        while len(bullets) < 2:
            bullets.append("See full paper for additional findings")

        ga_messages.append({
            "paper_no":    i,
            "title":       src["title"][:70] + "..." if len(src["title"]) > 70 else src["title"],
            "key_points":  bullets,
            "pubmed_link": pm_link,
            "authors":     src.get("authors", ""),
            "journal":     src.get("journal", ""),
        })

    # Initialise agent_outputs dict in run store
    run_store[run_id]["agent_outputs"] = {}

    def update(agent: str, pct: int, msg: str):
        run_store[run_id].update({
            "current_agent": agent,
            "progress":      pct,
            "status_msg":    msg,
        })
        time.sleep(random.uniform(1.8, 2.8))

    # ── Agent Alpha: PubMed Scraping + MA Library ─────────────────────────────
    # Step 2 in the new pipeline: PubMed search + MA Content Library check
    update("alpha", 10, "🔬 Agent Alpha: Querying PubMed with 3 search angles...")
    update("alpha", 22, "📚 Agent Alpha: Fetching paper metadata (authors, PMID, abstracts)...")
    update("alpha", 35, "🏥 Agent Alpha: Checking MA Content Library for internal documents...")
    update("alpha", 45, "📋 Agent Alpha: Compiling paper list with metadata...")

    # Alpha done → paper list with metadata (Step 3 output: show to user)
    run_store[run_id]["agent_outputs"]["alpha"] = {
        "papers":        sources,        # list of papers with title/authors/url/snippet
        "internal_docs": internal_docs,  # MA library documents found
        "paper_count":   len(sources),
        "internal_count": len(internal_docs),
        "summary":       (
            f"✅ {len(sources)} PubMed paper(s) found + "
            f"{len(internal_docs)} MA library document(s)"
        ),
    }

    # ── Agent Beta: Per-Paper Summaries ──────────────────────────────────────
    # Step 4: summarise each paper from Alpha's list
    update("beta", 55, "🧠 Agent Beta: Generating summary for each paper...")
    update("beta", 65, "📊 Agent Beta: Extracting key findings and evidence levels per paper...")

    # Beta done → per-paper summaries output (Step 4)
    run_store[run_id]["agent_outputs"]["beta"] = {
        "per_paper_summaries": [
            {
                "paper_no":    i + 1,
                "title":       src["title"][:80],
                "key_finding": src.get("snippet", "")[:200],
            }
            for i, src in enumerate(sources)
        ],
        "overall_finding": content["key_findings"][0] if content.get("key_findings") else "",
        "papers_summarised": len(sources),
        "summary": (
            f"✅ {len(sources)} paper(s) summarised · "
            f"Evidence strength: {content.get('evidence_quality', 'High')}"
        ),
    }

    # ── Agent Gamma: Shareable Content with Read More Links ──────────────────
    # Step 5: format shareable WhatsApp/email messages per paper with PubMed links
    update("gamma", 75, "✍️  Agent Gamma: Preparing shareable content per paper...")
    update("gamma", 85, "📱 Agent Gamma: Adding 'Read More' PubMed links to each message...")

    # Gamma done → shareable content per paper (Step 5)
    article      = content["short_article"]
    word_count   = len(article.split())
    excerpt_raw  = article[:230]
    excerpt      = excerpt_raw.rsplit(" ", 1)[0] if " " in excerpt_raw else excerpt_raw
    run_store[run_id]["agent_outputs"]["gamma"] = {
        "messages":        ga_messages,      # per-paper shareable messages with Read More links
        "article_excerpt": excerpt,          # kept for backward-compat with React UI
        "word_count":      word_count,
        "messages_count":  len(ga_messages),
        "summary": (
            f"✅ {len(ga_messages)} shareable message(s) prepared with PubMed 'Read More' links"
        ),
    }

    # ── Agent Delta: Publisher ────────────────────────────────────────────────
    update("delta", 92, "🗂️  Agent Delta: Generating structured JSON content card...")
    update("delta", 98, "✅ Agent Delta: Saving to Pinnacle Content Library...")

    # ── Build one content card per source paper ───────────────────────────────
    # Each card gets its own title, authors, pubmed_link, short_article with Read More
    per_paper_cards = []
    for i, src in enumerate(sources):
        pmid = ""
        src_url = src.get("url", "")
        if "pubmed.ncbi.nlm.nih.gov" in src_url:
            candidate = src_url.rstrip("/").split("/")[-1]
            if candidate.isdigit():
                pmid = candidate
        pm_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else src_url
        src_title   = src.get("title", f"{topic} — Paper {i+1}")
        src_authors = src.get("authors", f"International {specialty} Research Consortium, et al.")
        src_journal = src.get("journal", "PubMed Central / NCBI")
        src_snippet = src.get("snippet", "")

        # Build a per-paper short_article WITH Read More link
        paper_article = (
            f"RESEARCH UPDATE: {src_title}\n\n"
            f"{src_snippet}\n\n"
            f"This paper provides important insights for {specialty} practice in "
            f"{therapy_area}. The findings are directly relevant to clinical decision-making "
            f"and patient management in the Indian healthcare context.\n\n"
            f"---\n\n"
            f"📖 **Read the full article:** [{src_title}]({pm_link})\n\n"
            f"**Authors:** {src_authors}\n"
            f"**Journal:** {src_journal}\n\n"
            f"*— Pinnacle Research Team | Mankind Pharma*"
        )

        card = {
            "topic":        topic,
            "title":        src_title[:120],
            "specialty":    content.get("specialty", specialty),
            "therapy_area": content.get("therapy_area", therapy_area),
            "sub_category": content.get("sub_category", "Review Article"),
            "tags":         content.get("tags", [topic.split()[0], specialty, therapy_area]),
            "summary":      src_snippet[:300] if src_snippet else content.get("summary", ""),
            "key_findings":      content.get("key_findings", []),
            "clinical_insights": content.get("clinical_insights", ""),
            "recommendations":   content.get("recommendations", []),
            "emerging_trends":   content.get("emerging_trends", []),
            "evidence_quality":  content.get("evidence_quality", ""),
            "short_article":     paper_article,
            "authors":           src_authors,
            "pubmed_link":       pm_link,
            "source_journals":   src_journal,
            "pmid":              pmid or None,
            "doi":               content.get("doi"),
            "publication_date":  content.get("publication_date"),
            "relevant_doctor_specialties": content.get("relevant_doctor_specialties", specialty),
            "whatsapp_summary":  src_snippet[:200] if src_snippet else content.get("whatsapp_summary", ""),
        }
        per_paper_cards.append(card)

    # ── Pipeline complete ─────────────────────────────────────────────────────
    run_store[run_id].update({
        "status":        "completed",
        "progress":      100,
        "current_agent": "done",
        "status_msg":    "Pipeline complete. Content ready for MA review.",
        # Store ALL cards — app.py will save each one to SQLite
        "content":       per_paper_cards[0] if per_paper_cards else content,
        "all_cards":     per_paper_cards,
    })

    # Delta done → publish card preview for UI (one card per paper)
    # Build per-card summaries for the UI
    delta_cards_ui = []
    for j, pc in enumerate(per_paper_cards, 1):
        delta_cards_ui.append({
            "card_no":      j,
            "title":        pc.get("title", ""),
            "authors":      pc.get("authors", ""),
            "pubmed_link":  pc.get("pubmed_link", ""),
            "sub_category": pc.get("sub_category", ""),
            "tags":         pc.get("tags", [])[:5],
        })

    run_store[run_id]["agent_outputs"]["delta"] = {
        "card_title":    content["title"],
        "tags":          content["tags"],
        "sub_category":  content["sub_category"],
        "cards_saved":   len(per_paper_cards),
        "per_paper_cards": delta_cards_ui,
        "summary":       f"✅ {len(per_paper_cards)} content card(s) saved · Pending MA Review",
    }
