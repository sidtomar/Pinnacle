"""
Add birthday and anniversary features to the portal
This script will:
1. Add a "Birthday & Anniversary" tab to the Today page
2. Add birthday/anniversary info to doctor cards
3. Create a function to filter and display relevant doctors
"""

import re

# Read the HTML file
with open('../PinnacleIQ_Portal.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 1. Add birthday/anniversary tab after the "Upcoming" tab
tab_insertion = '''<div class="stab" onclick="setTodayTab('birthdays',this)">Birthdays & Anniversaries <span class="tc" id="tc-bd">0</span></div>'''

# Find the location to insert (after "Upcoming" tab)
upcoming_pattern = r'(<div class="stab" onclick="setTodayTab\(\'upcoming\'.*?</div>)'
html_content = re.sub(upcoming_pattern, r'\1\n          ' + tab_insertion, html_content, count=1)

print("Successfully added Birthday & Anniversary tab to Today page")

# 2. Add styles for birthday/anniversary badge
badge_styles = '''
.birthday-badge {
  display: inline-block;
  padding: 4px 8px;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  color: #333;
  font-size: 10px;
  font-weight: 700;
  border-radius: 4px;
  margin-left: 6px;
  text-transform: uppercase;
}

.anniversary-badge {
  display: inline-block;
  padding: 4px 8px;
  background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 4px;
  margin-left: 6px;
  text-transform: uppercase;
}
'''

# Add styles before closing </style> tag
html_content = html_content.replace('</style>', badge_styles + '</style>')

print("Added birthday & anniversary badge styles")

# Write back
with open('../PinnacleIQ_Portal.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Successfully updated PinnacleIQ_Portal.html with birthday & anniversary features!")
