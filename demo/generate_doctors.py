"""
generate_doctors.py
===================
Generates a realistic 100-doctor training database for PinnacleIQ demo.
10 doctors per specialization across Indian cities and hospitals.

Run:  python demo/generate_doctors.py
Output: demo/doctors.json

Before production: replace with live sync from Databricks
  (STORE_BACKEND=databricks → doctors table synced daily via ADF pipeline)
"""

import json, random
from datetime import date, timedelta

random.seed(42)   # reproducible output

# ── Helper ────────────────────────────────────────────────────────────────────
def rand_date(start="2025-01-01", end="2026-01-15"):
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return (s + timedelta(days=random.randint(0, (e - s).days))).isoformat()

def rand_phone():
    prefix = random.choice(["98", "99", "97", "96", "78", "77", "70", "91"])
    return f"+91-{prefix}{random.randint(10000000,99999999)}"

def rand_email(name, hospital):
    first = name.split()[1].lower()
    domain = hospital.lower().replace(" ", "").replace("'", "")[:12] + ".com"
    return f"{first}.{random.randint(10,99)}@{domain}"

# ── Master doctor list ────────────────────────────────────────────────────────
# (name, designation, specialty, sub_specialty, hospital, city, state, tier, ppd, yoe, channel, notes)
DOCTORS_RAW = [

    # ══ GENERAL MEDICINE ════════════════════════════════════════════════════
    ("Dr. Rajesh Kumar Sharma",  "Sr. Consultant",       "General Medicine", "Internal Medicine",       "Apollo Hospitals",          "New Delhi",  "Delhi",         "A", 45, 22, "whatsapp", "High prescriber, responds to WhatsApp; key opinion leader in South Delhi"),
    ("Dr. Priya Mehta",          "Consultant Physician", "General Medicine", "Infectious Disease",       "Fortis Hospital",           "Mumbai",     "Maharashtra",   "A", 38, 15, "whatsapp", "Strong follower of evidence-based updates; prefers concise cards"),
    ("Dr. Suresh Nair",          "Consultant",           "General Medicine", "Internal Medicine",       "Aster MIMS",                "Kochi",      "Kerala",        "B", 30, 12, "email",    "Active on email; attends monthly CME religiously"),
    ("Dr. Anjali Singh",         "Sr. Consultant",       "General Medicine", "Metabolic Disorders",     "Max Healthcare",            "Gurugram",   "Haryana",       "A", 50, 19, "whatsapp", "Very engaged; shares Pinnacle cards with resident doctors"),
    ("Dr. Vikram Patel",         "Consultant Physician", "General Medicine", "Preventive Medicine",     "Kokilaben Hospital",        "Mumbai",     "Maharashtra",   "B", 28, 10, "whatsapp", "Mid-tier; growing practice; open to new therapy updates"),
    ("Dr. Meera Pillai",         "Sr. Physician",        "General Medicine", "Internal Medicine",       "KIMS Hospital",             "Hyderabad",  "Telangana",     "A", 55, 25, "whatsapp", "Highest patient volume in cluster; very receptive to GP content"),
    ("Dr. Arun Bose",            "Consultant",           "General Medicine", "Internal Medicine",       "Medica Superspecialty",     "Kolkata",    "West Bengal",   "B", 32, 14, "email",    "Prefers detailed PDF reports; influential in peer group"),
    ("Dr. Sunita Agarwal",       "Sr. Consultant",       "General Medicine", "Geriatrics",              "Medanta",                   "Gurugram",   "Haryana",       "A", 40, 20, "whatsapp", "Focuses on elderly care; interested in polypharmacy content"),
    ("Dr. Rohit Malhotra",       "Consultant Physician", "General Medicine", "Internal Medicine",       "Fortis Hospital",           "Chandigarh", "Punjab",        "B", 35, 11, "whatsapp", "Young, tech-savvy; high WhatsApp engagement rate"),
    ("Dr. Divya Krishnan",       "Consultant",           "General Medicine", "Lifestyle Medicine",      "Manipal Hospital",          "Bangalore",  "Karnataka",     "B", 25, 8,  "email",    "New to Pinnacle; interested in lifestyle disease updates"),

    # ══ CARDIOLOGY ══════════════════════════════════════════════════════════
    ("Dr. Ashok Mahajan",        "Director — Cardiology","Cardiology",       "Interventional Cardiology","Narayana Health",           "Bangalore",  "Karnataka",     "A", 60, 28, "whatsapp", "Top KOL; influential at national cardiology conferences"),
    ("Dr. Kavita Reddy",         "Sr. Cardiologist",     "Cardiology",       "Heart Failure",           "Apollo Hospitals",          "Chennai",    "Tamil Nadu",    "A", 45, 20, "whatsapp", "Heart failure specialist; keen on SGLT2i and HFpEF updates"),
    ("Dr. Sanjay Gupta",         "Professor",            "Cardiology",       "Clinical Cardiology",     "AIIMS",                     "New Delhi",  "Delhi",         "A", 55, 30, "email",    "Academic leader; prefers journal-style evidence summaries"),
    ("Dr. Nandita Iyer",         "Consultant Cardiologist","Cardiology",     "Electrophysiology",       "Jaslok Hospital",           "Mumbai",     "Maharashtra",   "B", 30, 14, "whatsapp", "Arrhythmia specialist; moderate engagement"),
    ("Dr. Rajeev Menon",         "Sr. Consultant",       "Cardiology",       "Preventive Cardiology",   "Amrita Hospital",           "Kochi",      "Kerala",        "A", 48, 22, "whatsapp", "Strong advocate of preventive cardiology; shares content widely"),
    ("Dr. Pooja Saxena",         "Consultant",           "Cardiology",       "Echocardiography",        "Max Super Speciality",      "New Delhi",  "Delhi",         "B", 35, 12, "email",    "Young cardiologist building practice; interested in imaging updates"),
    ("Dr. Venkatesh Rajan",      "Head of Cardiology",   "Cardiology",       "Interventional Cardiology","MIOT International",        "Chennai",    "Tamil Nadu",    "A", 58, 26, "whatsapp", "Performs 200+ cath procedures/month; high prescriber for CV drugs"),
    ("Dr. Deepak Shrivastava",   "Sr. Consultant",       "Cardiology",       "Heart Failure",           "Fortis Hospital",           "Jaipur",     "Rajasthan",     "B", 42, 18, "whatsapp", "Covers large referral area in Rajasthan; tier-2 city KOL"),
    ("Dr. Shobha Rao",           "Professor of Cardiology","Cardiology",     "Cardiac Rehabilitation",  "Manipal Hospital",          "Bangalore",  "Karnataka",     "B", 28, 15, "email",    "Academic focus; involved in cardiac rehab research"),
    ("Dr. Amit Bhatt",           "Consultant Cardiologist","Cardiology",     "Structural Heart Disease","Kokilaben Hospital",        "Mumbai",     "Maharashtra",   "A", 50, 21, "whatsapp", "TAVI and structural procedures expert; high-value prescriber"),

    # ══ DIABETOLOGY / ENDOCRINOLOGY ═════════════════════════════════════════
    ("Dr. Anand Krishnamurthy",  "Consultant Diabetologist","Diabetology",   "Type 2 Diabetes",         "Diacon Hospital",           "Bangalore",  "Karnataka",     "A", 55, 24, "whatsapp", "Top diabetologist in Bangalore; prescribes GLP-1 RAs extensively"),
    ("Dr. Ritu Arora",           "Sr. Endocrinologist",  "Diabetology",      "Thyroid & Diabetes",      "Max Healthcare",            "New Delhi",  "Delhi",         "A", 48, 18, "whatsapp", "Very engaged with Pinnacle; frequently requests new content"),
    ("Dr. Girish Patel",         "Consultant",           "Diabetology",      "Obesity & Metabolic",     "Sterling Hospital",         "Ahmedabad",  "Gujarat",       "B", 35, 13, "whatsapp", "Obesity focused; interested in tirzepatide and GLP-1 updates"),
    ("Dr. Sharmila Nair",        "Sr. Consultant",       "Diabetology",      "Paediatric Endocrinology","Amrita Hospital",           "Kochi",      "Kerala",        "B", 30, 11, "email",    "Paediatric diabetes specialist; interested in ADA guideline updates"),
    ("Dr. Pramod Tripathi",      "Director",             "Diabetology",      "Diabetes Reversal",       "Freedom Diabetes Centre",   "Pune",       "Maharashtra",   "A", 60, 20, "whatsapp", "Pioneer in diabetes reversal programs; massive social media following"),
    ("Dr. Neha Joshi",           "Consultant Physician", "Diabetology",      "Type 1 & 2 Diabetes",    "Breach Candy Hospital",     "Mumbai",     "Maharashtra",   "B", 32, 9,  "whatsapp", "Young specialist; active in patient education; high digital engagement"),
    ("Dr. Subramaniam Pillai",   "Professor",            "Diabetology",      "Endocrinology",           "Apollo Hospitals",          "Chennai",    "Tamil Nadu",    "A", 52, 27, "email",    "Senior academic; preferred evidence summaries with citations"),
    ("Dr. Asha Kadam",           "Consultant Diabetologist","Diabetology",   "Gestational Diabetes",    "Ruby Hall Clinic",          "Pune",       "Maharashtra",   "B", 28, 10, "whatsapp", "GDM specialist; interested in inositol and PCOS-diabetes overlap"),
    ("Dr. Kartik Shah",          "Sr. Consultant",       "Diabetology",      "Insulin Therapy",         "Zydus Hospitals",           "Ahmedabad",  "Gujarat",       "B", 40, 15, "whatsapp", "Insulin optimisation expert; large private practice"),
    ("Dr. Lakshmi Venkataraman", "Consultant",           "Diabetology",      "Diabetic Complications",  "Narayana Health",           "Chennai",    "Tamil Nadu",    "A", 45, 19, "whatsapp", "Nephropathy & retinopathy focus; interested in SGLT2i renal data"),

    # ══ GYNAECOLOGY & OBSTETRICS ═════════════════════════════════════════════
    ("Dr. Shobha Gupta",         "Sr. Consultant",       "Gynaecology",      "High-Risk Obstetrics",    "Sitaram Bhartia Institute", "New Delhi",  "Delhi",         "A", 35, 23, "whatsapp", "High-risk pregnancy expert; KOL for north India gynaecology"),
    ("Dr. Padmaja Divakar",      "Consultant",           "Gynaecology",      "PCOS & Infertility",      "Cloudnine Hospital",        "Bangalore",  "Karnataka",     "A", 42, 17, "whatsapp", "PCOS expert; very interested in inositol vs metformin updates"),
    ("Dr. Usha Saraiya",         "President — FOGSI",    "Gynaecology",      "Menopause & HRT",         "Breach Candy Hospital",     "Mumbai",     "Maharashtra",   "A", 30, 35, "email",    "National gynaecology body president; highly influential speaker"),
    ("Dr. Kamala Selvaraj",      "Sr. Consultant",       "Gynaecology",      "Reproductive Medicine",   "Apollo Hospitals",          "Chennai",    "Tamil Nadu",    "A", 38, 22, "whatsapp", "IVF and reproductive medicine; interested in PCOS fertility data"),
    ("Dr. Rekha Daver",          "Consultant",           "Gynaecology",      "Laparoscopic Surgery",    "Lilavati Hospital",         "Mumbai",     "Maharashtra",   "B", 25, 18, "email",    "Surgical gynaecologist; moderate Pinnacle engagement"),
    ("Dr. Aruna Muralidhar",     "Sr. Consultant",       "Gynaecology",      "PCOS & Endometriosis",    "Fortis Hospital",           "Bangalore",  "Karnataka",     "B", 30, 14, "whatsapp", "PCOS subspecialist; shares content with junior doctors"),
    ("Dr. Nirmala Singh",        "Professor",            "Gynaecology",      "Obstetrics",              "KGMU",                      "Lucknow",    "Uttar Pradesh", "B", 45, 28, "email",    "Academic centre; trains residents; interested in ANC guideline updates"),
    ("Dr. Sudha Seshadri",       "Head of Department",   "Gynaecology",      "Uro-Gynaecology",         "Madras Medical College",    "Chennai",    "Tamil Nadu",    "A", 50, 30, "email",    "Senior academic; peer reviewer; prefers full research articles"),
    ("Dr. Prabha Desai",         "Consultant",           "Gynaecology",      "Adolescent Health",       "KEM Hospital",              "Mumbai",     "Maharashtra",   "B", 28, 12, "whatsapp", "Adolescent and PCOS clinic; interested in inositol for teens"),
    ("Dr. Hema Divakar",         "Director",             "Gynaecology",      "High-Risk Obstetrics",    "Cloudnine Hospital",        "Bangalore",  "Karnataka",     "A", 40, 25, "whatsapp", "National trainer for high-risk OB; Pinnacle early adopter"),

    # ══ PAEDIATRICS ════════════════════════════════════════════════════════
    ("Dr. Bakul Parekh",         "Consultant Paediatrician","Paediatrics",   "General Paediatrics",     "Surya Children's Hospital", "Mumbai",     "Maharashtra",   "A", 50, 28, "whatsapp", "Ex-IAP president; very high influence in paediatric community"),
    ("Dr. Dhanya Dharmapalan",   "Consultant",           "Paediatrics",      "Paediatric Infectious Disease","Apollo Navi Mumbai",  "Navi Mumbai","Maharashtra",   "B", 38, 14, "whatsapp", "Infection control specialist; interested in vaccine-preventable disease data"),
    ("Dr. Nitin Shah",           "Sr. Consultant",       "Paediatrics",      "Adolescent Medicine",     "Children's Hospital",       "Ahmedabad",  "Gujarat",       "A", 45, 22, "whatsapp", "Adolescent health focus; interested in nutrition and immunity content"),
    ("Dr. Geeta Gathwala",       "Professor",            "Paediatrics",      "Neonatology",             "PGIMS",                     "Rohtak",     "Haryana",       "B", 40, 25, "email",    "Neonatology expert; interested in preterm nutrition evidence"),
    ("Dr. Jacob Puliyel",        "Consultant",           "Paediatrics",      "Paediatric Medicine",     "St. Stephens Hospital",     "New Delhi",  "Delhi",         "B", 30, 30, "email",    "Senior paediatrician; vaccine policy researcher"),
    ("Dr. Piyush Gupta",         "Professor & HOD",      "Paediatrics",      "Paediatric Nutrition",    "UCMS & GTB Hospital",       "New Delhi",  "Delhi",         "A", 55, 27, "email",    "IAP nutrition expert; key contact for paediatric nutrition content"),
    ("Dr. Madhu Bhatt",          "Consultant",           "Paediatrics",      "Developmental Paediatrics","Sterling Hospital",         "Ahmedabad",  "Gujarat",       "B", 28, 10, "whatsapp", "Child development focus; growing practice"),
    ("Dr. Anuradha Khatri",      "Sr. Consultant",       "Paediatrics",      "Paediatric Pulmonology",  "Rainbow Children's",        "Hyderabad",  "Telangana",     "B", 35, 15, "whatsapp", "Respiratory disease in children; interested in allergy updates"),
    ("Dr. Suresh Birajdar",      "Consultant Paediatrician","Paediatrics",   "Neonatology",             "Wadia Children's Hospital", "Mumbai",     "Maharashtra",   "A", 42, 20, "whatsapp", "NICU expert; prescribes nutritional supplements extensively"),
    ("Dr. Anupama Borker",       "Sr. Consultant",       "Paediatrics",      "Paediatric Haematology",  "Manipal Hospital",          "Bangalore",  "Karnataka",     "B", 30, 13, "email",    "Onco-haematology; niche specialty; low volume but high engagement"),

    # ══ ORTHOPAEDICS ════════════════════════════════════════════════════════
    ("Dr. S. Rajasekaran",       "Chairman — Spine",     "Orthopaedics",     "Spine Surgery",           "Ganga Hospital",            "Coimbatore", "Tamil Nadu",    "A", 40, 35, "email",    "World-renowned spine surgeon; Spine Society past president"),
    ("Dr. Ashok Rajgopal",       "Chairman — Orthopaedics","Orthopaedics",   "Knee Replacement",        "Medanta",                   "Gurugram",   "Haryana",       "A", 35, 30, "whatsapp", "Highest volume TKR surgeon in India; key implant prescriber"),
    ("Dr. Raju Vaishya",         "Sr. Consultant",       "Orthopaedics",     "Sports Medicine",         "Indraprastha Apollo",       "New Delhi",  "Delhi",         "A", 38, 28, "whatsapp", "Celebrity patient surgeon; sports medicine expert; high media presence"),
    ("Dr. Satish Rao",           "Consultant",           "Orthopaedics",     "Joint Replacement",       "Manipal Hospital",          "Mangalore",  "Karnataka",     "B", 25, 14, "whatsapp", "Hip & knee replacement; tier-2 city practice"),
    ("Dr. Naresh Agarwal",       "Sr. Consultant",       "Orthopaedics",     "Trauma & Fracture",       "Fortis Hospital",           "New Delhi",  "Delhi",         "B", 30, 17, "email",    "Trauma specialist; interested in bone health and osteoporosis content"),
    ("Dr. Sachin Tapasvi",       "Consultant",           "Orthopaedics",     "Ligament & Sports",       "Pune Orthopedic Clinic",    "Pune",       "Maharashtra",   "A", 35, 16, "whatsapp", "Sports knee surgery expert; large social media following"),
    ("Dr. Milind Patil",         "Professor",            "Orthopaedics",     "Paediatric Orthopaedics", "KEM Hospital",              "Mumbai",     "Maharashtra",   "B", 28, 22, "email",    "Academic; paediatric bone disease focus"),
    ("Dr. Arun Bapat",           "Sr. Consultant",       "Orthopaedics",     "Hip Replacement",         "Deenanath Mangeshkar",      "Pune",       "Maharashtra",   "B", 30, 20, "whatsapp", "Hip replacement expert; Pune KOL"),
    ("Dr. Vikram Shah",          "Chairman — Orthopaedics","Orthopaedics",   "Joint Replacement",       "Shalby Hospitals",          "Ahmedabad",  "Gujarat",       "A", 45, 25, "whatsapp", "Chain hospital orthopaedics head; very high prescriber"),
    ("Dr. Manish Dhawan",        "Consultant",           "Orthopaedics",     "Shoulder & Elbow",        "Max Super Speciality",      "New Delhi",  "Delhi",         "B", 28, 12, "whatsapp", "Upper limb specialist; young growing practice"),

    # ══ OPHTHALMOLOGY ═══════════════════════════════════════════════════════
    ("Dr. Lalit Verma",          "Professor",            "Ophthalmology",    "Vitreo-Retina",           "AIIMS",                     "New Delhi",  "Delhi",         "A", 40, 30, "email",    "Retina expert; AIIMS faculty; writes national guidelines"),
    ("Dr. Sanjiv Mohan",         "Sr. Consultant",       "Ophthalmology",    "Glaucoma",                "Fortis Hospital",           "New Delhi",  "Delhi",         "A", 45, 24, "whatsapp", "Glaucoma subspecialist; interested in IOP management updates"),
    ("Dr. Pradeep Venkatesh",    "Professor",            "Ophthalmology",    "Retina & Uvea",           "Dr. RP Centre AIIMS",       "New Delhi",  "Delhi",         "A", 38, 22, "email",    "Uveitis and retina expert; publishes frequently in indexed journals"),
    ("Dr. Kim Ramasamy",         "Chairman",             "Ophthalmology",    "Cornea & Refractive",     "Aravind Eye Hospital",      "Madurai",    "Tamil Nadu",    "A", 60, 32, "whatsapp", "Aravind system — largest eye hospital network; massive influence"),
    ("Dr. Padmamalini Mahendradas","Sr. Consultant",     "Ophthalmology",    "Uveitis",                 "Narayana Nethralaya",       "Bangalore",  "Karnataka",     "B", 28, 16, "email",    "Uveitis expert; interested in autoimmune eye disease content"),
    ("Dr. Nikhil Nasta",         "Consultant",           "Ophthalmology",    "Cataract & Refractive",   "Nanavati Hospital",         "Mumbai",     "Maharashtra",   "B", 35, 13, "whatsapp", "High-volume cataract surgeon; interested in post-op drug protocols"),
    ("Dr. Meenakshi Swaminathan","Director",             "Ophthalmology",    "Cornea",                  "Sankara Nethralaya",        "Chennai",    "Tamil Nadu",    "A", 42, 28, "email",    "Sankara Nethralaya director; national cornea transplant leader"),
    ("Dr. Rajvardhan Azad",      "Professor",            "Ophthalmology",    "Vitreo-Retina",           "AIIMS",                     "New Delhi",  "Delhi",         "A", 35, 25, "email",    "Vitreoretinal surgery expert; researcher and author"),
    ("Dr. Savita Bhat",          "Sr. Consultant",       "Ophthalmology",    "Paediatric Ophthalmology","LV Prasad Eye Institute",   "Hyderabad",  "Telangana",     "B", 30, 14, "whatsapp", "Paediatric eye disease; interested in childhood myopia content"),
    ("Dr. Hanumantha Rao",       "Consultant",           "Ophthalmology",    "Glaucoma",                "LV Prasad Eye Institute",   "Hyderabad",  "Telangana",     "B", 38, 16, "whatsapp", "Glaucoma management; large outreach program in AP/Telangana"),

    # ══ NEUROLOGY ═══════════════════════════════════════════════════════════
    ("Dr. Sudhir Kumar",         "Director — Neurology", "Neurology",        "Headache & Migraine",     "Apollo Hospitals",          "Hyderabad",  "Telangana",     "A", 45, 22, "whatsapp", "Migraine and headache expert; very active on social media and Pinnacle"),
    ("Dr. Dheeraj Khurana",      "Professor",            "Neurology",        "Stroke",                  "PGIMER",                    "Chandigarh", "Punjab",        "A", 40, 24, "email",    "Stroke unit head; interested in acute stroke management content"),
    ("Dr. Vinit Suri",           "Chairman — Neurosciences","Neurology",     "Epilepsy",                "Indraprastha Apollo",       "New Delhi",  "Delhi",         "A", 38, 20, "whatsapp", "Epilepsy management expert; high prescriber for anti-epileptics"),
    ("Dr. Suresh Kumar",         "Professor",            "Neurology",        "Neurodegenerative Disease","NIMHANS",                   "Bangalore",  "Karnataka",     "A", 35, 25, "email",    "Parkinson's and dementia expert; academic leader"),
    ("Dr. Gagandeep Singh",      "Sr. Professor",        "Neurology",        "Neuroinfection",          "PGIMER",                    "Chandigarh", "Punjab",        "B", 30, 20, "email",    "CNS infections specialist; interested in antimicrobial content"),
    ("Dr. Uday Muthane",         "Consultant",           "Neurology",        "Movement Disorders",      "Parkinson's Research Centre","Bangalore", "Karnataka",     "B", 25, 28, "email",    "India's leading Parkinson's researcher; low volume, high influence"),
    ("Dr. P.N. Renjen",          "Chairman — Neurology", "Neurology",        "Stroke & Critical Care",  "Indraprastha Apollo",       "New Delhi",  "Delhi",         "A", 50, 30, "whatsapp", "Stroke ICU expert; media spokesperson for neurological emergencies"),
    ("Dr. Lekha Pandit",         "Professor",            "Neurology",        "Multiple Sclerosis",      "Goa Medical College",       "Panaji",     "Goa",           "B", 20, 22, "email",    "MS specialist; interested in DMT updates and neuroimmunology"),
    ("Dr. Jayanthi Mani",        "Consultant Neurologist","Neurology",       "General Neurology",       "King Edward Memorial",      "Mumbai",     "Maharashtra",   "B", 35, 15, "whatsapp", "General neurology; good engagement with clinical content"),
    ("Dr. Satish Khadilkar",     "Consultant",           "Neurology",        "Neuromuscular Disease",   "Bombay Hospital",           "Mumbai",     "Maharashtra",   "A", 40, 26, "whatsapp", "Neuromuscular disease expert; active in MDA India"),

    # ══ NEPHROLOGY ══════════════════════════════════════════════════════════
    ("Dr. Umesh Khanna",         "Consultant Nephrologist","Nephrology",     "Renal Transplant",        "Bombay Hospital",           "Mumbai",     "Maharashtra",   "A", 30, 35, "whatsapp", "Pioneer of renal transplant in India; very high influence"),
    ("Dr. Georgi Abraham",       "Director",             "Nephrology",       "CKD & Dialysis",          "Madras Medical Mission",    "Chennai",    "Tamil Nadu",    "A", 35, 30, "email",    "CKD expert; involved in national renal registry; writes guidelines"),
    ("Dr. Vivekanand Jha",       "Executive Director",   "Nephrology",       "CKD Research",            "George Institute",          "New Delhi",  "Delhi",         "A", 25, 28, "email",    "Global CKD researcher; SGLT2i renal protection expert"),
    ("Dr. Sanjeev Gulati",       "Principal Director",   "Nephrology",       "Kidney Transplant",       "Fortis Hospital",           "New Delhi",  "Delhi",         "A", 30, 25, "whatsapp", "Transplant nephrologist; interested in immunosuppressant updates"),
    ("Dr. Rajan Ravichandran",   "Director",             "Nephrology",       "Interventional Nephrology","MIOT International",        "Chennai",    "Tamil Nadu",    "A", 28, 22, "whatsapp", "AV fistula and dialysis access expert; good Pinnacle engagement"),
    ("Dr. Manjunath Hande",      "Professor",            "Nephrology",       "Glomerular Disease",      "Manipal Hospital",          "Manipal",    "Karnataka",     "B", 22, 18, "email",    "Glomerulonephritis specialist; academic focus"),
    ("Dr. Sanjay Pandit",        "Consultant",           "Nephrology",       "CKD & Hypertension",      "Nanavati Hospital",         "Mumbai",     "Maharashtra",   "B", 28, 15, "whatsapp", "CKD-hypertension overlap; interested in SGLT2i renal data"),
    ("Dr. Anand Sharma",         "Sr. Consultant",       "Nephrology",       "Renal Medicine",          "Medanta",                   "Gurugram",   "Haryana",       "B", 30, 16, "whatsapp", "Good engagement; part of Medanta's large nephrology team"),
    ("Dr. Sidharth Sethi",       "Consultant",           "Nephrology",       "Paediatric Nephrology",   "Kidney & Urology Institute","New Delhi",  "Delhi",         "B", 20, 10, "whatsapp", "Paediatric kidney disease; young specialist; growing network"),
    ("Dr. Narayan Prasad",       "Professor",            "Nephrology",       "Kidney Transplant",       "SGPGI",                     "Lucknow",    "Uttar Pradesh", "A", 35, 24, "email",    "Academic transplant centre; key prescriber in UP/Bihar catchment"),

    # ══ DERMATOLOGY ═════════════════════════════════════════════════════════
    ("Dr. Kiran Godse",          "Sr. Consultant",       "Dermatology",      "Medical & Cosmetic Derm", "Bombay Hospital",           "Mumbai",     "Maharashtra",   "A", 50, 20, "whatsapp", "High-volume practice; interested in acne biologics and retinoid updates"),
    ("Dr. Niti Khunger",         "Professor",            "Dermatology",      "Cosmetic Dermatology",    "VMMC & Safdarjung",         "New Delhi",  "Delhi",         "A", 40, 22, "email",    "Cosmetic procedures expert; writes IADVL guidelines"),
    ("Dr. Bela Shah",            "Consultant",           "Dermatology",      "Paediatric Dermatology",  "MP Shah Medical College",   "Jamnagar",   "Gujarat",       "B", 30, 18, "whatsapp", "Paediatric skin conditions; interested in atopic dermatitis content"),
    ("Dr. Deepali Bhardwaj",     "Associate Professor",  "Dermatology",      "Hair & Scalp Disorders",  "AIIMS",                     "New Delhi",  "Delhi",         "B", 28, 14, "email",    "Hair loss and alopecia specialist; moderate engagement"),
    ("Dr. Rajeev Joshi",         "Consultant",           "Dermatology",      "Pigmentary Disorders",    "Lilavati Hospital",         "Mumbai",     "Maharashtra",   "B", 35, 16, "whatsapp", "Melasma and vitiligo; interested in topical agent updates"),
    ("Dr. Rashmi Sarkar",        "Professor",            "Dermatology",      "Acne & Pigmentation",     "Maulana Azad Medical College","New Delhi", "Delhi",         "A", 42, 24, "email",    "Acne treatment KOL; writes chapters in Indian dermatology texts"),
    ("Dr. Shyam Verma",          "Consultant",           "Dermatology",      "General Dermatology",     "Niramaya Skin Clinic",      "Vadodara",   "Gujarat",       "B", 45, 20, "whatsapp", "High-volume tier-2 practice; interested in antifungal & acne content"),
    ("Dr. Chandra Sekhar",       "Sr. Consultant",       "Dermatology",      "Aesthetic Dermatology",   "Apollo Hospitals",          "Hyderabad",  "Telangana",     "B", 38, 15, "whatsapp", "Laser and aesthetic focus; interested in cosmeceutical updates"),
    ("Dr. Venkataram Mysore",    "Director",             "Dermatology",      "Hair Transplant & Lasers","Venkat Center for Skin",    "Bangalore",  "Karnataka",     "A", 40, 28, "whatsapp", "Hair transplant pioneer in India; high media visibility"),
    ("Dr. Nalini Vijayaraghavan","Sr. Consultant",       "Dermatology",      "Psoriasis & Autoimmune",  "Apollo Hospitals",          "Chennai",    "Tamil Nadu",    "A", 35, 21, "whatsapp", "Biologics in psoriasis expert; interested in IL-17/IL-23 updates"),
]

# ── Engagement parameters per tier ────────────────────────────────────────────
TIER_PARAMS = {
    "A": {"eng": (72, 96), "pin": (78, 98), "recv": (10, 28)},
    "B": {"eng": (42, 72), "pin": (45, 78), "recv": (3,  14)},
    "C": {"eng": (20, 45), "pin": (22, 50), "recv": (0,   6)},
}

def build_doctor(idx, row):
    (name, desig, spec, sub, hosp, city, state, tier, ppd, yoe, channel, notes) = row
    p = TIER_PARAMS[tier]
    eng  = random.randint(*p["eng"])
    pin  = random.randint(*p["pin"])
    recv = random.randint(*p["recv"])
    joined = rand_date("2025-01-10", "2026-01-20")
    # last contacted within last 60 days
    last = rand_date("2026-03-15", "2026-05-22")

    return {
        "id":                 f"DOC{idx:03d}",
        "name":               name,
        "designation":        desig,
        "specialty":          spec,
        "sub_specialty":      sub,
        "hospital":           hosp,
        "city":               city,
        "state":              state,
        "tier":               tier,
        "whatsapp":           rand_phone(),
        "email":              rand_email(name, hosp),
        "patients_per_day":   ppd,
        "years_experience":   yoe,
        "preferred_channel":  channel,
        "engagement_score":   eng,
        "pinnacle_score":     pin,
        "content_received":   recv,
        "pinnacle_joined":    joined,
        "last_contacted":     last,
        "status":             "active",
        "notes":              notes,
    }

# ── Build and save ─────────────────────────────────────────────────────────────
doctors = [build_doctor(i + 1, row) for i, row in enumerate(DOCTORS_RAW)]

specialties = sorted(set(d["specialty"] for d in doctors))
cities      = sorted(set(d["city"]      for d in doctors))

output = {
    "generated_at": str(date.today()),
    "total":        len(doctors),
    "specialties":  specialties,
    "cities":       cities,
    "tier_breakdown": {
        t: len([d for d in doctors if d["tier"] == t])
        for t in ["A", "B", "C"]
    },
    "doctors": doctors,
}

import pathlib
out_path = pathlib.Path(__file__).parent / "doctors.json"
out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"[OK] Written {len(doctors)} doctors -> {out_path}")
print(f"   Specialties ({len(specialties)}): {', '.join(specialties)}")
print(f"   Tiers: { {t:len([d for d in doctors if d['tier']==t]) for t in ['A','B','C']} }")
print(f"   Cities: {len(cities)}")
