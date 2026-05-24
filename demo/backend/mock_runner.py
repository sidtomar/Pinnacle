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


# ── Alpha research sources per topic (shown after Alpha completes) ─────────────

ALPHA_SOURCES = {
    "SGLT2": [
        {
            "title": "EMPEROR-Reduced 3-Year Extended Follow-Up: Empagliflozin in HFrEF",
            "journal": "New England Journal of Medicine",
            "url": "https://www.nejm.org/doi/10.1056/NEJMoa2107519",
            "snippet": "Empagliflozin reduces HF hospitalisation by 30% and CV death by 18% at 3 years, irrespective of diabetes status or ejection fraction",
        },
        {
            "title": "DAPA-HF Extended Analysis: Dapagliflozin Across the EF Spectrum (HFrEF + HFpEF)",
            "journal": "The Lancet",
            "url": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(23)00512-8",
            "snippet": "Dapagliflozin effect consistent across full ejection fraction spectrum — first evidence-based option for HFpEF patients",
        },
        {
            "title": "2025 ESC Heart Failure Guidelines: Class I Recommendation for SGLT2i in All HF",
            "journal": "European Heart Journal (ESC Guidelines)",
            "url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Heart-Failure",
            "snippet": "All HF patients should receive SGLT2 inhibitor regardless of diabetes status or EF — Class I, Level A evidence",
        },
        {
            "title": "SGLT2i Meta-Analysis: 94,820 Patients Across T2DM, HF, and CKD Populations",
            "journal": "Journal of the American College of Cardiology (JACC)",
            "url": "https://www.jacc.org/doi/10.1016/j.jacc.2023.04.034",
            "snippet": "30% reduction in first HF hospitalisation, 14% reduction in CV death (HR 0.86) — consistent benefit across all subgroups",
        },
        {
            "title": "Cochrane Review: SGLT2 Inhibitors for Heart Failure — Systematic Evidence Synthesis",
            "journal": "Cochrane Database of Systematic Reviews",
            "url": "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013812",
            "snippet": "High-certainty evidence: SGLT2i reduce HF hospitalisation and CV mortality in both diabetic and non-diabetic HF patients",
        },
        {
            "title": "Indian HF Registry 2024: SGLT2i Reduces 30-Day Readmission by 27%",
            "journal": "Indian Heart Journal / PubMed (NCBI)",
            "url": "https://pubmed.ncbi.nlm.nih.gov/38291234",
            "snippet": "Real-world Indian data (n=1,240) confirms 27% reduction in 30-day HF readmission with empagliflozin and dapagliflozin",
        },
        {
            "title": "SGLT2i Renal Protection in HF: eGFR Decline Slowed by 1.6 mL/min/year",
            "journal": "BMJ (British Medical Journal)",
            "url": "https://www.bmj.com/content/382/bmj-2023-074256",
            "snippet": "SGLT2 inhibitors slow eGFR decline by 1.6 mL/min/year vs placebo — renal protection confirmed independent of glycaemic status",
        },
        {
            "title": "Embase Systematic Review: SGLT2i Safety Profile Across 120 RCTs",
            "journal": "Embase / European Journal of Heart Failure",
            "url": "https://www.embase.com/",
            "snippet": "Genital infections (3.1x risk) manageable with hygiene counselling; DKA risk minimal in non-diabetic HF population",
        },
        {
            "title": "WHO Model List: SGLT2 Inhibitors Added as Essential Medicines for HF (2025)",
            "journal": "WHO IRIS (International Repository)",
            "url": "https://iris.who.int/handle/10665/371432",
            "snippet": "WHO includes dapagliflozin on Essential Medicines List for heart failure — landmark recognition of global access importance",
        },
        {
            "title": "ClinicalTrials.gov: SOLOIST-WHF — Sotagliflozin in Acute Heart Failure",
            "journal": "ClinicalTrials.gov Registry",
            "url": "https://clinicaltrials.gov/study/NCT03521934",
            "snippet": "Dual SGLT1+2 inhibition: sotagliflozin reduces HF events by 33% vs placebo when initiated during acute hospitalisation",
        },
    ],

    "GLP-1": [
        {
            "title": "GLP-1 RA Meta-Analysis 2025: 34 RCTs, n=87,420 — Superior Glycaemic + CV Control",
            "journal": "Diabetes Care (ADA)",
            "url": "https://diabetesjournals.org/care/article/48/1/S1",
            "snippet": "Semaglutide delivers HbA1c reduction of 1.8% vs 1.1% for DPP-4i; 33% MACE reduction in CV-risk population sustained at 5 years",
        },
        {
            "title": "SUSTAIN-6 5-Year Extension: Sustained Cardiovascular Protection with Semaglutide",
            "journal": "New England Journal of Medicine",
            "url": "https://www.nejm.org/doi/10.1056/NEJMoa1607141",
            "snippet": "33% sustained reduction in MACE (CV death, non-fatal MI, non-fatal stroke) at 5-year follow-up in T2DM with established CVD",
        },
        {
            "title": "ADA/EASD 2025 Consensus: GLP-1 RAs First-Line Alongside Metformin in T2DM+CVD/HF/CKD",
            "journal": "Diabetologia / Diabetes Care",
            "url": "https://diabetesjournals.org/care/article/48/Supplement_1/S1",
            "snippet": "Updated 2025 consensus recommends GLP-1 RAs regardless of baseline HbA1c when ASCVD, heart failure, or CKD is present",
        },
        {
            "title": "PIONEER-PLUS: Oral Semaglutide 50mg Beats Injectable Liraglutide Head-to-Head",
            "journal": "The Lancet",
            "url": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(23)01127-3",
            "snippet": "Oral semaglutide 50 mg achieves −1.5% HbA1c and −8.7 kg at 52 weeks — superior to injectable liraglutide across all endpoints",
        },
        {
            "title": "Cochrane Review: GLP-1 Receptor Agonists for Type 2 Diabetes — 176 Trials",
            "journal": "Cochrane Database of Systematic Reviews",
            "url": "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013120",
            "snippet": "High-certainty evidence: GLP-1 RAs reduce all-cause mortality (RR 0.88), CV death (RR 0.85), and HbA1c across all comparators",
        },
        {
            "title": "GLP-1 RAs in South Asian T2DM: Indian Multi-Centre Cohort Study (n=2,840)",
            "journal": "PubMed (NCBI) / Journal of Diabetes India",
            "url": "https://pubmed.ncbi.nlm.nih.gov/39102847",
            "snippet": "GLP-1 RAs achieve 1.6% HbA1c reduction in Indian patients with BMI 23–27 — efficacy confirmed at lower BMI than Western thresholds",
        },
        {
            "title": "Embase: Dulaglutide Renal Protection in T2DM+CKD (AWARD-7 Full Dataset)",
            "journal": "Embase / American Journal of Kidney Diseases",
            "url": "https://www.embase.com/",
            "snippet": "Dulaglutide shows superiority in eGFR 30–60 range; 15% slower eGFR decline vs insulin glargine over 52 weeks",
        },
        {
            "title": "Scopus Analysis: GLP-1 RA Adherence — Once-Weekly vs Daily Formulations",
            "journal": "Scopus / Patient Preference and Adherence",
            "url": "https://www.scopus.com/",
            "snippet": "Once-weekly formulations achieve 94% adherence vs 71% for daily injections — largest real-world adherence gap in any injectable class",
        },
        {
            "title": "BMJ Meta-Analysis: Tirzepatide (GIP+GLP-1) — SURPASS Programme Results",
            "journal": "BMJ (British Medical Journal)",
            "url": "https://www.bmj.com/content/382/bmj-2023-074256",
            "snippet": "Tirzepatide 15mg: −2.4% HbA1c and −11.2 kg weight loss — superior to all GLP-1 RA comparators in head-to-head trials",
        },
        {
            "title": "ClinicalTrials.gov: RETATRUTIDE Phase 3 — Triple Agonist GIP/GLP-1/Glucagon",
            "journal": "ClinicalTrials.gov Registry",
            "url": "https://clinicaltrials.gov/study/NCT05524935",
            "snippet": "Phase 3 programme underway; Phase 2 showed −24.2% body weight at 48 weeks — potential game-changer for obesity+T2DM",
        },
    ],

    "PCOS": [
        {
            "title": "Myo-Inositol vs Metformin in PCOS: 2025 Systematic Review of 22 RCTs (n=3,180)",
            "journal": "PubMed (NCBI) / Fertility and Sterility",
            "url": "https://pubmed.ncbi.nlm.nih.gov/38761294",
            "snippet": "Myo-inositol matches metformin for insulin sensitisation: 12% vs 34% GI adverse events; menstrual regularity 78% vs 64% at 6 months",
        },
        {
            "title": "ESHRE/ASRM 2025 PCOS Guidelines: Combined Inositol Recommended as First-Line",
            "journal": "Human Reproduction / ESHRE",
            "url": "https://www.eshre.eu/Guidelines-and-Legal/Guidelines/Polycystic-Ovarian-Syndrome",
            "snippet": "Myo + d-chiro inositol at 40:1 ratio recommended as first-line for lean PCOS and metformin-intolerant patients per updated ESHRE guidance",
        },
        {
            "title": "Cochrane Review: Inositol for PCOS — Reproductive, Metabolic and Hormonal Outcomes",
            "journal": "Cochrane Database of Systematic Reviews",
            "url": "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014296",
            "snippet": "Pregnancy rates 34% (inositol) vs 29% (metformin); AMH improvement 23% vs 11% — clinically meaningful for fertility-seeking patients",
        },
        {
            "title": "Embase: Lean PCOS Phenotype — Inositol Superiority in BMI <23 Asian Cohorts",
            "journal": "Embase / Gynecological Endocrinology",
            "url": "https://www.embase.com/",
            "snippet": "Lean PCOS (BMI <23) responds poorly to metformin; inositol delivers consistent insulin sensitisation in Asian phenotype patients",
        },
        {
            "title": "Inositol in Indian PCOS: Multi-Centre Cohort Study (n=420, BMI <23 Subgroup)",
            "journal": "PubMed India / Journal of Obstetrics & Gynaecology India",
            "url": "https://pubmed.ncbi.nlm.nih.gov/39021847",
            "snippet": "First large Indian dataset confirms inositol effectiveness in lean PCOS — a gap previously unaddressed in local clinical evidence",
        },
        {
            "title": "Scopus: Gut Microbiome Modulation as Adjunct to Inositol in PCOS — 2024 Review",
            "journal": "Scopus / Journal of Clinical Endocrinology & Metabolism",
            "url": "https://www.scopus.com/",
            "snippet": "Microbiome dysbiosis identified in 68% of PCOS patients; probiotic co-administration with inositol shows additive metabolic benefit",
        },
        {
            "title": "BMJ: PCOS Diagnosis Delay in India — Average 3.2 Years Post-Symptom Onset",
            "journal": "BMJ Open / British Medical Journal",
            "url": "https://bmjopen.bmj.com/",
            "snippet": "Indian PCOS patients experience 3.2-year average diagnosis delay; early screening protocol could prevent metabolic progression in 40% of cases",
        },
        {
            "title": "Europe PMC: Adolescent PCOS — Safety and Efficacy of Inositol in Teens",
            "journal": "Europe PMC / Pediatric Endocrinology Reviews",
            "url": "https://europepmc.org/",
            "snippet": "Inositol safe and effective in adolescent PCOS (age 14–18); no growth or hormonal disruption detected at 12-month follow-up",
        },
        {
            "title": "ClinicalTrials.gov: Inositol + NAC Combination — Phase 3 Indian Trial (Ongoing)",
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
    return [
        {
            "title": f"2025 Systematic Review: {topic} — 14 RCTs, n=21,400",
            "journal": "PubMed Central / NCBI",
            "url": "https://pmc.ncbi.nlm.nih.gov/",
            "snippet": f"Comprehensive meta-analysis confirms efficacy of targeted intervention in {therapy_area} with favourable safety profile across diverse populations",
        },
        {
            "title": f"2025 {specialty} Society Guidelines on {therapy_area} Management",
            "journal": f"International Journal of {specialty}",
            "url": "https://pubmed.ncbi.nlm.nih.gov/",
            "snippet": f"Updated clinical practice guidelines recommend proactive, evidence-based management in {therapy_area} with combination therapy approaches",
        },
        {
            "title": f"Indian Cohort Study: {keyword} Therapy in {specialty} Practice (n=1,840)",
            "journal": "Indian Journal of Medical Research / PubMed India",
            "url": "https://www.ijmr.org.in/",
            "snippet": "Real-world Indian data confirms efficacy matching global trial results with locally relevant dosing and tolerability profile",
        },
        {
            "title": f"Real-World Evidence: {keyword} in Routine {specialty} Practice — 2024 Registry Data",
            "journal": "Journal of Clinical Medicine / PubMed",
            "url": "https://www.mdpi.com/journal/jcm",
            "snippet": "Registry data from 8,200 patients shows 40% improvement in primary outcomes vs standard of care; adherence improved with once-daily regimens",
        },
    ]


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
    Updates run_store[run_id] at each step — including per-agent outputs
    (sources, findings, article excerpt, card preview) for live UI display.
    """

    # ── Determine content, sources, and internal docs upfront ────────────────
    key = next((k for k in MOCK_LIBRARY if k.upper() in topic.upper()), None)
    content       = MOCK_LIBRARY[key] if key else _generic_content(topic, specialty, therapy_area)
    sources       = ALPHA_SOURCES.get(key) if key else _generic_sources(topic, specialty, therapy_area)
    internal_docs = ALPHA_INTERNAL_DOCS.get(key) if key else _generic_internal_docs(topic)

    # Initialise agent_outputs dict in run store
    run_store[run_id]["agent_outputs"] = {}

    def update(agent: str, pct: int, msg: str):
        run_store[run_id].update({
            "current_agent": agent,
            "progress":      pct,
            "status_msg":    msg,
        })
        time.sleep(random.uniform(1.8, 2.8))

    # ── Agent Alpha: Research ─────────────────────────────────────────────────
    update("alpha", 10, "🔍 Agent Alpha: Searching PubMed and web sources...")
    update("alpha", 22, "📂 Agent Alpha: Reading internal documents from Research folder...")
    update("alpha", 35, "📄 Agent Alpha: Reading and ranking relevant papers...")
    update("alpha", 45, "📝 Agent Alpha: Consolidating research article...")

    # Alpha done → publish sources + internal_docs output for UI
    run_store[run_id]["agent_outputs"]["alpha"] = {
        "sources":       sources,
        "internal_docs": internal_docs,
        "summary":       f"{len(sources)} web sources + {len(internal_docs)} internal documents",
    }

    # ── Agent Beta: Insights ──────────────────────────────────────────────────
    update("beta", 55, "🧠 Agent Beta: Extracting key insights and clinical findings...")
    update("beta", 65, "📊 Agent Beta: Formulating clinical recommendations...")

    # Beta done → publish findings output for UI
    run_store[run_id]["agent_outputs"]["beta"] = {
        "findings": content["key_findings"],
        "summary":  f"{len(content['key_findings'])} key insights extracted",
    }

    # ── Agent Gamma: Content Writer ───────────────────────────────────────────
    update("gamma", 75, "✍️  Agent Gamma: Writing doctor-friendly short article...")
    update("gamma", 85, "📱 Agent Gamma: Formatting for WhatsApp & email delivery...")

    # Gamma done → publish article excerpt for UI (clean word boundary)
    article      = content["short_article"]
    word_count   = len(article.split())
    excerpt_raw  = article[:230]
    excerpt      = excerpt_raw.rsplit(" ", 1)[0] if " " in excerpt_raw else excerpt_raw
    run_store[run_id]["agent_outputs"]["gamma"] = {
        "article_excerpt": excerpt,
        "word_count":      word_count,
        "summary":         f"Article written · {word_count} words",
    }

    # ── Agent Delta: Publisher ────────────────────────────────────────────────
    update("delta", 92, "🗂️  Agent Delta: Generating structured JSON content card...")
    update("delta", 98, "✅ Agent Delta: Saving to Pinnacle Content Library...")

    # ── Pipeline complete ─────────────────────────────────────────────────────
    run_store[run_id].update({
        "status":        "completed",
        "progress":      100,
        "current_agent": "done",
        "status_msg":    "Pipeline complete. Content ready for MA review.",
        "content": {
            "topic":        topic,
            "specialty":    specialty,
            "therapy_area": therapy_area,
            **content,
        },
    })

    # Delta done → publish card preview for UI
    run_store[run_id]["agent_outputs"]["delta"] = {
        "card_title":   content["title"],
        "tags":         content["tags"],
        "sub_category": content["sub_category"],
        "summary":      "Content card saved · Pending MA Review",
    }
