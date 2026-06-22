import json
from datetime import datetime, timedelta
import random

# Read existing doctors.json
with open('demo/doctors.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

doctors = data.get('doctors', [])

# Generate random birthdays and anniversaries
random.seed(42)  # For consistency

for doctor in doctors:
    # Random birthday (between 25-70 years old)
    years_ago = random.randint(25, 70)
    random_day_of_year = random.randint(1, 365)
    birth_date = datetime(datetime.now().year - years_ago, 1, 1) + timedelta(days=random_day_of_year)
    doctor['birthday'] = birth_date.strftime('%Y-%m-%d')
    
    # Random anniversary (between 1-30 years of marriage)
    years_married = random.randint(1, 30)
    random_anniversary_day = random.randint(1, 365)
    anniversary_date = datetime(datetime.now().year - years_married, 1, 1) + timedelta(days=random_anniversary_day)
    doctor['anniversary'] = anniversary_date.strftime('%Y-%m-%d')

# Write back
with open('demo/doctors.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Updated doctors.json with birthday and anniversary fields")
print(f"Total doctors updated: {len(doctors)}")
print(f"\nSample doctor:")
print(f"  Name: {doctors[0]['name']}")
print(f"  Birthday: {doctors[0]['birthday']}")
print(f"  Anniversary: {doctors[0]['anniversary']}")
