#!/usr/bin/env python3
"""
Script to validate and enrich company-developer mappings using reference data.
Uses official team CSV files from data/ folder to verify and improve mappings.
"""

import csv
from collections import defaultdict
from rapidfuzz import fuzz

# Reference team files
TEAM_FILES = {
    'Lutra Consulting': 'data/lutra_consulting_team.csv',
    'OPENGIS.ch': 'data/opengis_team.csv',
    'Oslandia': 'data/oslandia_team.csv',
    'North Road': 'data/north_road_team.csv',
    'Kartoza': 'data/kartoza_team.csv',
    'Faunalia': 'data/faunalia_team.csv',
    'QCooperative': 'data/qcooperative_team.csv',
    'Spatialys': 'data/spatialys_team.csv',
    '3Liz': 'data/3liz_team.csv',
}

# Current mapping
CURRENT_MAPPING = 'output/companies_developers.csv'
OUTPUT_REPORT = 'output/validation_report.txt'

def load_reference_teams():
    """Load reference team data from CSV files."""
    teams = defaultdict(list)
    
    for company, filepath in TEAM_FILES.items():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Extract name from different column formats
                    name = row.get('name', '').strip()
                    if name:
                        teams[company].append(name)
            print(f"✅ Loaded {len(teams[company])} members from {company}")
        except FileNotFoundError:
            print(f"⚠️  File not found: {filepath}")
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
    
    return teams

def load_current_mapping():
    """Load current company-developer mapping."""
    mapping = defaultdict(list)
    
    try:
        with open(CURRENT_MAPPING, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company = row['company']
                developer = row['developer']
                features = int(row['feature_count'])
                mapping[company].append((developer, features))
        print(f"✅ Loaded current mapping with {len(mapping)} companies")
    except FileNotFoundError:
        print(f"❌ File not found: {CURRENT_MAPPING}")
        return None
    
    return mapping

def find_best_match(developer_name, reference_names, threshold=85):
    """Find the best matching name from reference list."""
    if not reference_names:
        return None, 0
    
    best_match = None
    best_score = 0
    
    for ref_name in reference_names:
        # Try different similarity metrics
        ratio = fuzz.ratio(developer_name.lower(), ref_name.lower())
        partial = fuzz.partial_ratio(developer_name.lower(), ref_name.lower())
        token_sort = fuzz.token_sort_ratio(developer_name.lower(), ref_name.lower())
        
        # Use the best score
        score = max(ratio, partial, token_sort)
        
        if score > best_score:
            best_score = score
            best_match = ref_name
    
    if best_score >= threshold:
        return best_match, best_score
    
    return None, best_score

def validate_mappings():
    """Validate current mappings against reference data."""
    
    print("\n🚀 Starting validation of company-developer mappings")
    print("=" * 70)
    
    # Load data
    print("\n📖 Loading reference team data...")
    reference_teams = load_reference_teams()
    
    print("\n📖 Loading current mappings...")
    current_mapping = load_current_mapping()
    
    if not current_mapping:
        return
    
    # Validation results
    validated = defaultdict(list)
    suggestions = defaultdict(list)
    not_in_reference = defaultdict(list)
    missing_from_mapping = defaultdict(list)
    
    print("\n🔍 Validating mappings...")
    
    for company, developers in current_mapping.items():
        if company not in reference_teams:
            # No reference data for this company
            for dev, features in developers:
                not_in_reference[company].append((dev, features, "No reference data"))
            continue
        
        ref_names = reference_teams[company]
        
        for dev, features in developers:
            # Check if developer is in reference list (exact match)
            if dev in ref_names:
                validated[company].append((dev, features, 100))
            else:
                # Try fuzzy matching
                match, score = find_best_match(dev, ref_names, threshold=85)
                
                if match:
                    # Found a similar name
                    suggestions[company].append((dev, match, score, features))
                else:
                    # Not found in reference
                    not_in_reference[company].append((dev, features, f"Best match score: {score:.1f}%"))
        
        # Check for missing developers (in reference but not in mapping)
        mapped_devs = {dev for dev, _ in developers}
        for ref_name in ref_names:
            # Check if this reference name matches any mapped developer
            found = False
            for mapped_dev in mapped_devs:
                score = fuzz.ratio(ref_name.lower(), mapped_dev.lower())
                if score >= 90:  # High threshold for reverse matching
                    found = True
                    break
            
            if not found:
                missing_from_mapping[company].append(ref_name)
    
    # Generate report
    print(f"\n💾 Generating validation report: {OUTPUT_REPORT}")
    
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("COMPANY-DEVELOPER MAPPING VALIDATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        # Summary
        total_validated = sum(len(devs) for devs in validated.values())
        total_suggestions = sum(len(devs) for devs in suggestions.values())
        total_not_found = sum(len(devs) for devs in not_in_reference.values())
        total_missing = sum(len(devs) for devs in missing_from_mapping.values())
        
        f.write("📊 SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"✅ Validated (exact matches): {total_validated}\n")
        f.write(f"💡 Suggestions (fuzzy matches): {total_suggestions}\n")
        f.write(f"❓ Not in reference data: {total_not_found}\n")
        f.write(f"🔍 Missing from mapping: {total_missing}\n")
        f.write("\n")
        
        # Validated developers
        if validated:
            f.write("=" * 70 + "\n")
            f.write("✅ VALIDATED DEVELOPERS (Exact matches with reference data)\n")
            f.write("=" * 70 + "\n\n")
            
            for company in sorted(validated.keys()):
                f.write(f"\n🏢 {company}\n")
                for dev, features, score in sorted(validated[company], key=lambda x: x[1], reverse=True):
                    f.write(f"   ✓ {dev} ({features} features)\n")
        
        # Suggestions for normalization
        if suggestions:
            f.write("\n" + "=" * 70 + "\n")
            f.write("💡 SUGGESTIONS FOR NORMALIZATION (Fuzzy matches)\n")
            f.write("=" * 70 + "\n\n")
            
            for company in sorted(suggestions.keys()):
                f.write(f"\n🏢 {company}\n")
                for current, suggested, score, features in sorted(suggestions[company], key=lambda x: x[2], reverse=True):
                    f.write(f"   '{current}' → '{suggested}' (similarity: {score:.1f}%, {features} features)\n")
        
        # Not found in reference
        if not_in_reference:
            f.write("\n" + "=" * 70 + "\n")
            f.write("❓ DEVELOPERS NOT IN REFERENCE DATA\n")
            f.write("=" * 70 + "\n")
            f.write("(These might be past employees, contributors, or data quality issues)\n\n")
            
            for company in sorted(not_in_reference.keys()):
                f.write(f"\n🏢 {company}\n")
                for dev, features, note in sorted(not_in_reference[company], key=lambda x: x[1], reverse=True):
                    f.write(f"   ? {dev} ({features} features) - {note}\n")
        
        # Missing from mapping
        if missing_from_mapping:
            f.write("\n" + "=" * 70 + "\n")
            f.write("🔍 EMPLOYEES IN REFERENCE BUT NOT IN FEATURE MAPPING\n")
            f.write("=" * 70 + "\n")
            f.write("(These team members might not have contributed to QGIS features in the analyzed versions)\n\n")
            
            for company in sorted(missing_from_mapping.keys()):
                f.write(f"\n🏢 {company} ({len(missing_from_mapping[company])} members)\n")
                for ref_name in sorted(missing_from_mapping[company]):
                    f.write(f"   - {ref_name}\n")
    
    # Console output
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    print(f"✅ Validated (exact matches): {total_validated}")
    print(f"💡 Suggestions (fuzzy matches): {total_suggestions}")
    print(f"❓ Not in reference data: {total_not_found}")
    print(f"🔍 Missing from mapping: {total_missing}")
    
    if suggestions:
        print("\n💡 Top normalization suggestions:")
        all_suggestions = []
        for company, sug_list in suggestions.items():
            for current, suggested, score, features in sug_list:
                all_suggestions.append((company, current, suggested, score, features))
        
        for company, current, suggested, score, features in sorted(all_suggestions, key=lambda x: x[4], reverse=True)[:10]:
            print(f"   [{company}] '{current}' → '{suggested}' ({score:.1f}%, {features} features)")
    
    print(f"\n📁 Full report saved to: {OUTPUT_REPORT}")
    print("\n🎉 Validation completed!")

if __name__ == '__main__':
    validate_mappings()
