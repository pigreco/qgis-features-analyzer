#!/usr/bin/env python3
"""
Script to normalize developer names in the developed_by column using fuzzy matching.
Similar to OpenRefine's clustering functionality.
"""

import csv
import re
from collections import defaultdict, Counter
from rapidfuzz import fuzz, process

# Input and output files
INPUT_CSV = 'output/qgis_features_raw.csv'
OUTPUT_CSV = 'output/qgis_features_normalized_dev.csv'
MAPPING_FILE = 'output/developer_normalizations.txt'

# Fuzzy matching threshold (0-100)
SIMILARITY_THRESHOLD = 85

def extract_developer_name(developer_string):
    """
    Extract clean developer name from various formats.
    Handles: "Developer (Company)", "Company (Developer)", "Developer", etc.
    """
    if not developer_string or developer_string == 'Not specified':
        return None
    
    # Remove quotes
    developer_string = developer_string.strip('"').strip()
    
    # Skip if it's a collaboration (multiple names)
    if any(sep in developer_string for sep in [' & ', ' and ', ', ']):
        return developer_string  # Keep as is for now
    
    # Pattern: "Name (Company)" or "Company (Name)"
    match = re.search(r'^(.+?)\s*\(([^)]+)\)$', developer_string)
    if match:
        first = match.group(1).strip()
        second = match.group(2).strip()
        
        # Common company keywords
        company_keywords = ['lutra', 'opengis', 'oslandia', 'kartoza', 'north road',
                           'faunalia', 'qcooperative', 'spatialys', '3liz', 'qgis',
                           'consulting', 'gmbh', 'sarl']
        
        first_lower = first.lower()
        second_lower = second.lower()
        
        # If first part looks like a company, second is the name
        if any(kw in first_lower for kw in company_keywords):
            return second
        # If second part looks like a company, first is the name
        elif any(kw in second_lower for kw in company_keywords):
            return first
        # If "with" is in second part, it's likely "Developer (with Company)"
        elif 'with' in second_lower:
            return first
        else:
            # Default: assume "Name (Company)" format
            return first
    
    return developer_string

def normalize_name_basic(name):
    """Apply basic normalizations to a name."""
    if not name:
        return name
    
    # Known typos and variations
    normalizations = {
        'Martian Dobias': 'Martin Dobias',
        'Alex Bruy': 'Alexander Bruy',
        'Belgacem Nedjima': 'Nedjima Belgacem',
        'Nyall Dawson': 'Nyall Dawson',
        'Matthias Kuhn': 'Matthias Kuhn',
        'Martin Dobiaš': 'Martin Dobias',
        'Loïc Bartoletti': 'Loïc Bartoletti',
        'Loic Bartoletti': 'Loïc Bartoletti',
        'Mathieu Pellerin': 'Mathieu Pellerin',
        'Germán Carrillo': 'Germán Carrillo',
        'German Carrillo': 'Germán Carrillo',
        'René-Luc D\'Hont': 'René-Luc D\'Hont',
        'Rene-Luc D\'Hont': 'René-Luc D\'Hont',
        'Alessandro Pasotti': 'Alessandro Pasotti',
        'Sandro Santilli': 'Sandro Santilli',
    }
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Check known normalizations
    if name in normalizations:
        return normalizations[name]
    
    return name

def find_fuzzy_clusters(names, threshold=85):
    """
    Group similar names using fuzzy matching.
    Returns a dictionary: original_name -> canonical_name
    """
    # Filter out None and empty strings
    names = [n for n in names if n]
    
    if not names:
        return {}
    
    # Count occurrences
    name_counts = Counter(names)
    unique_names = list(name_counts.keys())
    
    # Dictionary to store mappings
    name_mapping = {}
    processed = set()
    
    print(f"🔍 Analyzing {len(unique_names)} unique developer names...")
    
    for i, name in enumerate(unique_names):
        if name in processed:
            continue
        
        # Find similar names
        similar = []
        for other_name in unique_names:
            if other_name == name or other_name in processed:
                continue
            
            # Calculate similarity
            ratio = fuzz.ratio(name.lower(), other_name.lower())
            
            if ratio >= threshold:
                similar.append((other_name, ratio, name_counts[other_name]))
        
        if similar:
            # Add the current name
            similar.append((name, 100, name_counts[name]))
            
            # Sort by frequency (most common first)
            similar.sort(key=lambda x: x[2], reverse=True)
            
            # Use the most common variant as canonical
            canonical = similar[0][0]
            
            print(f"\n📋 Cluster {len(name_mapping) + 1} (canonical: '{canonical}'):")
            for variant, ratio, count in similar:
                if variant != canonical:
                    print(f"   - '{variant}' (similarity: {ratio}%, count: {count}) → '{canonical}'")
                    name_mapping[variant] = canonical
                    processed.add(variant)
                else:
                    print(f"   ✓ '{canonical}' (count: {count})")
            
            processed.add(canonical)
    
    return name_mapping

def normalize_developers():
    """Main function to normalize developer names."""
    
    print("🚀 Starting developer name normalization")
    print("=" * 70)
    
    # Step 1: Extract all developer names
    print("\n📖 Step 1: Reading and extracting developer names...")
    
    all_developers = []
    rows = []
    
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                dev = row['developed_by']
                if dev and dev != 'Not specified':
                    all_developers.append(dev)
        
        print(f"✅ Read {len(rows)} rows, found {len(all_developers)} developer entries")
        
    except FileNotFoundError:
        print(f"❌ File {INPUT_CSV} not found!")
        return
    
    # Step 2: Extract clean names
    print("\n🧹 Step 2: Extracting clean developer names...")
    
    clean_names = []
    for dev in all_developers:
        name = extract_developer_name(dev)
        if name:
            # Apply basic normalizations
            name = normalize_name_basic(name)
            clean_names.append(name)
    
    print(f"✅ Extracted {len(clean_names)} clean names")
    
    # Step 3: Find fuzzy clusters
    print(f"\n🔎 Step 3: Finding similar names (threshold: {SIMILARITY_THRESHOLD}%)...")
    
    fuzzy_mapping = find_fuzzy_clusters(clean_names, threshold=SIMILARITY_THRESHOLD)
    
    print(f"\n✅ Found {len(fuzzy_mapping)} normalizations")
    
    # Step 4: Apply normalizations to original data
    print("\n✏️  Step 4: Applying normalizations to data...")
    
    normalization_stats = defaultdict(int)
    
    for row in rows:
        original = row['developed_by']
        
        if original and original != 'Not specified':
            # Extract clean name
            clean_name = extract_developer_name(original)
            
            if clean_name:
                # Apply basic normalization
                clean_name = normalize_name_basic(clean_name)
                
                # Apply fuzzy normalization if found
                if clean_name in fuzzy_mapping:
                    normalized = fuzzy_mapping[clean_name]
                    normalization_stats[f"{clean_name} → {normalized}"] += 1
                    
                    # Reconstruct the full string with normalized name
                    # Keep the company part if present
                    match = re.search(r'\(([^)]+)\)$', original)
                    if match:
                        company = match.group(1)
                        row['developed_by'] = f"{normalized} ({company})"
                    else:
                        row['developed_by'] = normalized
    
    # Step 5: Save normalized data
    print(f"\n💾 Step 5: Saving normalized data to {OUTPUT_CSV}...")
    
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"✅ Saved {len(rows)} rows to {OUTPUT_CSV}")
    
    # Step 6: Save normalization mapping
    print(f"\n📝 Step 6: Saving normalization mapping to {MAPPING_FILE}...")
    
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        f.write("DEVELOPER NAME NORMALIZATIONS\n")
        f.write("=" * 70 + "\n\n")
        
        if fuzzy_mapping:
            f.write(f"Found {len(fuzzy_mapping)} normalizations:\n\n")
            for original, canonical in sorted(fuzzy_mapping.items()):
                count = normalization_stats.get(f"{original} → {canonical}", 0)
                f.write(f"  '{original}' → '{canonical}' ({count} occurrences)\n")
        else:
            f.write("No fuzzy normalizations needed - all names are already consistent!\n")
    
    print(f"✅ Saved normalization mapping")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Total rows processed: {len(rows)}")
    print(f"Developer entries: {len(all_developers)}")
    print(f"Unique clean names: {len(set(clean_names))}")
    print(f"Normalizations applied: {len(fuzzy_mapping)}")
    print(f"Total changes: {sum(normalization_stats.values())}")
    
    if normalization_stats:
        print("\n📈 Top 10 normalizations:")
        for norm, count in sorted(normalization_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {count}× {norm}")
    
    print("\n🎉 Normalization completed!")
    print(f"📁 Normalized data: {OUTPUT_CSV}")
    print(f"📁 Mapping details: {MAPPING_FILE}")

if __name__ == '__main__':
    normalize_developers()
