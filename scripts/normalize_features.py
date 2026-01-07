#!/usr/bin/env python3
"""
Script to normalize QGIS features data from raw CSV.
Reads the raw CSV file and applies normalization rules to developer names.

Script per normalizzare i dati delle funzionalità QGIS dal CSV grezzo.
Legge il file CSV grezzo e applica regole di normalizzazione ai nomi degli sviluppatori.
"""

import csv
import re
import os

INPUT_CSV = "output/qgis_features_raw.csv"
OUTPUT_CSV = "output/qgis_features_normalized.csv"

def normalize_developer_name(name):
    """
    Normalize developer names according to specific rules:
    1. Nyall or Nyall Dawson → Nyall Dawson
    2. Mathieu or Mathieu Pellerin → Mathieu Pellerin
    3. Alessandro → Alessandro Pasotti
    4. Alexander or Alex Bruy → Alexander Bruy
    5. Even → Even Rouault
    6. Loïc → Loïc Bartoletti
    7. Martin → Martin Dobias
    8. Matthias → Matthias Kuhn
    9. North Road → Nyall Dawson
    10. Julien → Julien Cabieces
    11. Paul / OSLANDIA - Paul / Pau Blottiere → Paul Blottiere
    12. jef-n → Jürgen Fischer
    13. Sandro → Sandro Santilli
    14. Salvatore → Salvatore Larosa
    15. Denis → Denis Rouzaud
    16. Etienne/Étienne → Étienne Trimaille
    17. Andrea → Andrea Giudiceandrea
    18. Ismail → Ismail Sunni
    19. Juergen E. Fischer / Jürgen Fischer in collaboration with → Jürgen Fischer
    20. Nathan → Nathan Woodrow
    21. Matteo Ghetta (starts with) → Matteo Ghetta
    22. Marco → Marco Bernasocchi
    23. All names with "Lutra" → Lutra Consulting
    24. All names with "OPENGIS.ch" → OPENGIS.ch
    25. All names with "Kartoza" → Kartoza
    26. Empty names → Not specified
    27. Remove (North Road), (North), (Lutra Consulting), (Lutra), etc.
    28. Remove trailing ' /'
    """
    if not name or name == "Not specified":
        return name
    
    original_name = name
    
    # First, check if there's OPENGIS.ch in the name (before removing it)
    if 'opengis.ch' in name.lower() or 'opengis' in name.lower():
        return 'OPENGIS.ch'
    
    # Kartoza (any name with Kartoza) → Kartoza
    if 'kartoza' in name.lower():
        return 'Kartoza'
    
    # Remove company references in parentheses BEFORE normalization
    # (North Road), (North), (Lutra Consulting), (Lutra), etc.
    patterns_to_remove = [
        r'\s*\(North Road\)',
        r'\s*\(North\)',
        r'\s*\(Lutra Consulting\)',
        r'\s*\(Lutra\)',
        r'\s*\(OPENGIS\.ch\)',
        r'\s*\(Kartoza\)',
        r'\s*\(Oslandia\)',
        r'\s*\(OSLANDIA\)',
        r'\s*\(Faunalia\)',
        r'\s*\(www\.kartoza\.com\)',
        r'\s*\(http[s]?://[^\)]+\)',
    ]
    
    for pattern in patterns_to_remove:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Remove "OSLANDIA - " prefix
    name = re.sub(r'^OSLANDIA\s*-\s*', '', name, flags=re.IGNORECASE)
    
    # Remove "in collaboration with" and similar
    name = re.sub(r'\s+in collaboration with.*$', '', name, flags=re.IGNORECASE)
    
    # Normalize specific names
    name = name.strip()
    
    # If name is empty after cleaning, return "Not specified"
    if not name or name == '':
        return 'Not specified'
    
    name_lower = name.lower()
    
    # North Road (alone) → Nyall Dawson
    if name_lower == 'north road':
        return 'Nyall Dawson'
    
    # jef-n → Jürgen Fischer
    if 'jef-n' in name_lower or name_lower == 'jef-n':
        return 'Jürgen Fischer'
    
    # Juergen E. Fischer or Jürgen Fischer → Jürgen Fischer
    if 'juergen' in name_lower or 'jürgen' in name_lower:
        return 'Jürgen Fischer'
    
    # Lutra (any name with Lutra) → Lutra Consulting
    if 'lutra' in name_lower:
        return 'Lutra Consulting'
    
    # Denis (starts with Denis) → Denis Rouzaud
    if name_lower.startswith('denis'):
        return 'Denis Rouzaud'
    
    # Etienne/Étienne → Étienne Trimaille
    if name_lower.startswith('etienne') or name_lower.startswith('étienne'):
        return 'Étienne Trimaille'
    
    # Matteo Ghetta (starts with) → Matteo Ghetta
    if name_lower.startswith('matteo ghetta') or name_lower.startswith('matteo'):
        if 'ghetta' in name_lower or name_lower == 'matteo':
            return 'Matteo Ghetta'
    
    # Andrea → Andrea Giudiceandrea
    if name_lower == 'andrea' or (name_lower.startswith('andrea') and 'giudiceandrea' not in name_lower and len(name_lower.split()) == 1):
        return 'Andrea Giudiceandrea'
    elif 'andrea' in name_lower and 'giudiceandrea' in name_lower:
        return 'Andrea Giudiceandrea'
    
    # Ismail → Ismail Sunni
    if name_lower == 'ismail' or (name_lower.startswith('ismail') and 'sunni' not in name_lower and len(name_lower.split()) == 1):
        return 'Ismail Sunni'
    elif 'ismail' in name_lower and 'sunni' in name_lower:
        return 'Ismail Sunni'
    
    # Nathan → Nathan Woodrow
    if name_lower == 'nathan' or (name_lower.startswith('nathan') and 'woodrow' not in name_lower and len(name_lower.split()) == 1):
        return 'Nathan Woodrow'
    elif 'nathan' in name_lower and 'woodrow' in name_lower:
        return 'Nathan Woodrow'
    
    # Marco → Marco Bernasocchi
    if name_lower == 'marco' or (name_lower.startswith('marco') and 'bernasocchi' not in name_lower and len(name_lower.split()) == 1):
        return 'Marco Bernasocchi'
    elif 'marco' in name_lower and 'bernasocchi' in name_lower:
        return 'Marco Bernasocchi'
    
    # Salvatore → Salvatore Larosa
    if name_lower == 'salvatore' or (name_lower.startswith('salvatore') and 'larosa' not in name_lower and len(name_lower.split()) == 1):
        return 'Salvatore Larosa'
    elif 'salvatore' in name_lower and 'larosa' in name_lower:
        return 'Salvatore Larosa'
    
    # Nyall Dawson
    if 'nyall' in name_lower:
        return 'Nyall Dawson'
    
    # Mathieu Pellerin
    elif 'mathieu' in name_lower:
        return 'Mathieu Pellerin'
    
    # Alessandro Pasotti
    elif name_lower == 'alessandro' or (name_lower.startswith('alessandro') and 'pasotti' not in name_lower):
        return 'Alessandro Pasotti'
    elif 'alessandro' in name_lower and 'pasotti' in name_lower:
        return 'Alessandro Pasotti'
    
    # Alexander Bruy (also handles Alex Bruy)
    elif name_lower in ['alexander', 'alex bruy', 'alexander bruy']:
        return 'Alexander Bruy'
    elif (name_lower.startswith('alexander') or name_lower.startswith('alex')) and 'bruy' in name_lower:
        return 'Alexander Bruy'
    
    # Even Rouault
    elif name_lower == 'even' or (name_lower.startswith('even') and 'rouault' not in name_lower and len(name_lower.split()) == 1):
        return 'Even Rouault'
    elif 'even' in name_lower and 'rouault' in name_lower:
        return 'Even Rouault'
    
    # Loïc Bartoletti
    elif 'loïc' in name_lower or 'loic' in name_lower:
        if 'bartoletti' not in name_lower:
            return 'Loïc Bartoletti'
        else:
            return 'Loïc Bartoletti'
    
    # Martin Dobias
    elif name_lower == 'martin' or (name_lower.startswith('martin') and 'dobias' not in name_lower and len(name_lower.split()) == 1):
        return 'Martin Dobias'
    elif 'martin' in name_lower and 'dobias' in name_lower:
        return 'Martin Dobias'
    
    # Matthias Kuhn
    elif name_lower == 'matthias' or (name_lower.startswith('matthias') and 'kuhn' not in name_lower and len(name_lower.split()) == 1):
        return 'Matthias Kuhn'
    elif 'matthias' in name_lower and 'kuhn' in name_lower:
        return 'Matthias Kuhn'
    
    # Julien Cabieces
    elif name_lower == 'julien' or (name_lower.startswith('julien') and 'cabieces' not in name_lower and len(name_lower.split()) == 1):
        return 'Julien Cabieces'
    elif 'julien' in name_lower and 'cabieces' in name_lower:
        return 'Julien Cabieces'
    
    # Paul Blottiere (handles Paul, Pau Blottiere, OSLANDIA - Paul)
    elif name_lower in ['paul', 'pau blottiere']:
        return 'Paul Blottiere'
    elif 'paul' in name_lower and 'blottiere' in name_lower:
        return 'Paul Blottiere'
    elif 'pau' in name_lower and 'blottiere' in name_lower:
        return 'Paul Blottiere'
    
    # Sandro Santilli
    elif name_lower == 'sandro' or (name_lower.startswith('sandro') and 'santilli' not in name_lower and len(name_lower.split()) == 1):
        return 'Sandro Santilli'
    elif 'sandro' in name_lower and 'santilli' in name_lower:
        return 'Sandro Santilli'
    
    # Clean multiple spaces and trailing commas
    name = re.sub(r'\s+', ' ', name).strip()
    name = name.rstrip(',').strip()
    
    # Remove trailing ' /'
    name = re.sub(r'\s*/\s*$', '', name).strip()
    
    # Final check: if after all cleaning the name is empty
    if not name or name == '':
        return 'Not specified'
    
    return name

def normalize_csv(input_file, output_file):
    """Read raw CSV and create normalized version"""
    
    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found!")
        print(f"   Run extract_raw_features.py first to generate the raw data.")
        return
    
    print(f"📖 Reading raw data from {input_file}...")
    
    # Read input CSV
    features = []
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        features = list(reader)
    
    print(f"   Found {len(features)} features to normalize")
    
    # Apply normalization
    print(f"\n🔧 Applying normalization rules...")
    normalized_count = 0
    
    for feature in features:
        original_dev = feature['developed_by']
        normalized_dev = normalize_developer_name(original_dev)
        
        if original_dev != normalized_dev:
            normalized_count += 1
            if normalized_count <= 10:  # Show first 10 examples
                print(f"   '{original_dev}' → '{normalized_dev}'")
        
        feature['developed_by'] = normalized_dev
    
    if normalized_count > 10:
        print(f"   ... and {normalized_count - 10} more normalizations")
    
    print(f"\n   Total normalizations applied: {normalized_count}")
    
    # Save normalized CSV
    print(f"\n💾 Saving normalized data to {output_file}...")
    
    fieldnames = ['version', 'version_name', 'release_date', 'category', 'feature_name', 
                  'funded_by', 'funded_by_link', 'developed_by', 'developed_by_link', 'md_file']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(features)
    
    print(f"✅ Saved {len(features)} normalized features")
    
    # Statistics
    print("\n" + "=" * 70)
    print("📊 NORMALIZATION STATISTICS")
    print("=" * 70)
    
    # Count developers
    developers = {}
    for f in features:
        d = f['developed_by']
        if d != "Not specified":
            developers[d] = developers.get(d, 0) + 1
    
    print(f"\n👨‍💻 Top 15 developers (after normalization):")
    for dev, count in sorted(developers.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"   {dev}: {count} features")
    
    # Count funders
    funders = {}
    for f in features:
        fund = f['funded_by']
        if fund != "Not specified":
            funders[fund] = funders.get(fund, 0) + 1
    
    print(f"\n💰 Top 15 funders:")
    for funder, count in sorted(funders.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"   {funder}: {count} features")
    
    print(f"\n📁 Normalized CSV saved: {os.path.abspath(output_file)}")

def main():
    """Main function"""
    print("🚀 Starting data normalization")
    print("=" * 70)
    
    normalize_csv(INPUT_CSV, OUTPUT_CSV)
    
    print("\n🎉 Normalization completed!")

if __name__ == "__main__":
    main()
