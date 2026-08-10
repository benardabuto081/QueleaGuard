Write-Host "=== 1. Git log since last confirmed commit (5795792) ===" -ForegroundColor Cyan
git log --oneline 5795792..HEAD

Write-Host "`n=== 2. Git status (uncommitted changes) ===" -ForegroundColor Cyan
git status

Write-Host "`n=== 3. All Decision Log entries (checking for duplicates/unexpected additions) ===" -ForegroundColor Cyan
Get-Content docs\assumptions_and_decision_log.md | Select-String "^## Log Entry"

Write-Host "`n=== 4. Pseudo-absence dataset state ===" -ForegroundColor Cyan
python -c "
import pandas as pd
pa = pd.read_csv('data/processed/pseudo_absences_final.csv')
print('Total records:', len(pa))
print('Month-only dates remaining:', pa['eventDate'].astype(str).str.match(r'^\d{4}-\d{2}$').sum())
print('Sample dates:', pa['eventDate'].head(3).tolist())
"

Write-Host "`n=== 5. Rainfall extraction completeness (presence) ===" -ForegroundColor Cyan
python -c "
import pandas as pd
r = pd.read_csv('data/processed/rainfall_features.csv')
print('Presence rainfall records:', len(r))
"

Write-Host "`n=== 6. Rainfall extraction completeness (pseudo-absence) ===" -ForegroundColor Cyan
python -c "
import pandas as pd
r = pd.read_csv('data/processed/rainfall_features_pseudo_absence.csv')
print('Pseudo-absence rainfall records:', len(r))
print('Incomplete (days_with_data < 90):', (r['days_with_data'] < 90).sum())
"

Write-Host "`n=== 7. CHIRPS cache year range (checking for silent extension to 1981) ===" -ForegroundColor Cyan
python -c "
import glob, re
files = glob.glob('data/external/chirps_cache/**/*.tif.gz', recursive=True)
years = sorted(set(re.search(r'(\d{4})\.\d{2}\.\d{2}', f).group(1) for f in files))
print('Years present in cache:', years[0], 'to', years[-1])
print('Total files:', len(files))
"

Write-Host "`n=== 8. Any new/unexpected script files in src/ ===" -ForegroundColor Cyan
git status --porcelain src/ 2>$null
dir src\*.py | Select-Object Name, LastWriteTime | Sort-Object LastWriteTime -Descending | Select-Object -First 15
