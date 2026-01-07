#!/usr/bin/env python3
"""
Script to extract companies and their associated developers from QGIS features CSV.
Creates a mapping of companies to developers with normalization of similar company names.
"""

import csv
import re
from collections import defaultdict

INPUT_CSV = "output/qgis_features_normalized_dev.csv"
OUTPUT_CSV = "output/companies_developers.csv"
OUTPUT_TXT = "output/companies_developers.txt"

def normalize_company_name(company):
    """
    Normalize company names to handle variations and typos.
    Returns a standardized version of the company name.
    """
    if not company or company == "Not specified":
        return company
    
    # Dictionary of known variations and their canonical forms
    company_mappings = {
        # OPENGIS variations
        'opengis.ch': 'OPENGIS.ch',
        'opengis': 'OPENGIS.ch',
        'opengisch': 'OPENGIS.ch',
        'opengis.ch gmbh': 'OPENGIS.ch',
        
        # Lutra Consulting variations
        'lutra consulting': 'Lutra Consulting',
        'lutraconsulting': 'Lutra Consulting',
        'lutra': 'Lutra Consulting',
        
        # Oslandia variations
        'oslandia': 'Oslandia',
        'oslandia -': 'Oslandia',
        
        # North Road variations
        'north road': 'North Road',
        'north road consulting': 'North Road',
        
        # Kartoza variations
        'kartoza': 'Kartoza',
        'for kartoza': 'Kartoza',
        
        # Faunalia variations
        'faunalia': 'Faunalia',
        
        # 3Liz variations
        '3liz': '3Liz',
        '3liz.com': '3Liz',
        
        # QGIS variations
        'qgis.org donors and sponsors': 'QGIS.ORG donors and sponsors',
        'qgis.org': 'QGIS.ORG',
        'qgis grant program': 'QGIS Grant Program',
        'qgis': 'QGIS',
        
        # iMHere Asia variations
        'imhere asia': 'iMHere Asia',
        'imhere-asia': 'iMHere Asia',
        
        # QCooperative variations
        'qcooperative': 'QCooperative',
        'qcooperative /': 'QCooperative',
        'itopen / qcooperative': 'QCooperative',
        
        # Spatialys variations
        'spatialys': 'Spatialys',
        
        # Swiss QGIS user group variations
        'swiss qgis user group': 'Swiss QGIS User Group',
        'swiss qgis user-group': 'Swiss QGIS User Group',
        'the swiss qgis user group': 'Swiss QGIS User Group',
        'qgis swiss user group': 'Swiss QGIS User Group',
        
        # Bordeaux variations
        'bordeaux metropole': 'Bordeaux Métropole',
        'bordeaux métropôle': 'Bordeaux Métropole',
        'bordeaux métrôpole': 'Bordeaux Métropole',
        'métropôle de bordeaux': 'Bordeaux Métropole',
        
        # Lille variations
        'métropole européenne de lille': 'Métropole Européenne de Lille',
        'métropole de lille': 'Métropole Européenne de Lille',
        'lille metropole': 'Métropole Européenne de Lille',
        'metropole de lille': 'Métropole Européenne de Lille',
        
        # Ifremer
        'ifremer': 'Ifremer',
        
        # ARPA Piemonte variations
        'arpa piemonte': 'ARPA Piemonte',
        '**arpa piemonte**': 'ARPA Piemonte',
        'a.r.p.a. piemonte': 'ARPA Piemonte',
    }
    
    # Normalize to lowercase for matching
    company_lower = company.lower().strip()
    
    # Remove common prefixes/suffixes that don't affect identity
    company_lower = re.sub(r'\s*\(.*?\)\s*', '', company_lower)  # Remove parentheses content
    company_lower = re.sub(r'\s*@.*$', '', company_lower)  # Remove @ mentions
    company_lower = re.sub(r'\s*\*\*\s*', '', company_lower)  # Remove markdown bold
    company_lower = company_lower.strip()
    
    # Check if we have a known mapping
    if company_lower in company_mappings:
        return company_mappings[company_lower]
    
    # If not in mappings, return original with basic cleanup
    result = company.strip()
    result = re.sub(r'\s*\*\*\s*', '', result)  # Remove markdown bold
    result = re.sub(r'\s+', ' ', result)  # Normalize spaces
    
    return result

def is_company_name(text):
    """Check if text looks like a company name"""
    company_keywords = ['lutra', 'opengis', 'oslandia', 'kartoza', 'north road', 
                       'faunalia', 'qcooperative', 'spatialys', '3liz', 'qgis']
    text_lower = text.lower().replace(' ', '')
    return any(keyword.replace(' ', '') in text_lower for keyword in company_keywords)

def extract_companies_developers():
    """Extract and map companies to their developers"""
    
    # Dictionary: company -> set of developers
    company_developers = defaultdict(set)
    # Dictionary: (company, developer) -> count of features
    company_developer_features = defaultdict(int)
    
    # Known name normalizations for developers
    developer_normalizations = {
        'Martian Dobias': 'Martin Dobias',
        'Alex Bruy': 'Alexander Bruy',
        'Belgacem Nedjima': 'Nedjima Belgacem',
    }
    
    print("🔍 Reading CSV file...")
    
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                developer = row['developed_by'].strip()
                
                if not developer or developer == 'Not specified':
                    continue
                
                # Skip entries with collaborations (multiple developers/companies)
                if any(separator in developer for separator in [' & ', ' and ', ', ', ' with ']):
                    continue
                
                # Handle "Company / Developer" pattern
                if ' / ' in developer:
                    parts = developer.split(' / ')
                    if len(parts) == 2 and is_company_name(parts[0]):
                        company = parts[0].strip()
                        dev_name = parts[1].strip().strip('"')
                        normalized_company = normalize_company_name(company)
                        dev_name = developer_normalizations.get(dev_name, dev_name)
                        company_developers[normalized_company].add(dev_name)
                        company_developer_features[(normalized_company, dev_name)] += 1
                        continue
                
                # Skip entries that are just company names without developers
                if is_company_name(developer) and '(' not in developer:
                    continue
                
                # Pattern to extract company from "Developer (Company)"
                match = re.search(r'^(.+?)\s*\(([^)]+)\)$', developer)
                
                if match:
                    first_part = match.group(1).strip().strip('"')
                    second_part = match.group(2).strip()
                    
                    # Check for inverted pattern: "Company (Developer)"
                    if is_company_name(first_part) and not is_company_name(second_part):
                        company = first_part
                        dev_name = second_part
                    else:
                        # Normal pattern: "Developer (Company)"
                        dev_name = first_part
                        company = second_part
                    
                    # Skip if company is a URL or contains "with" (collaboration indicator)
                    if not company.startswith('http') and 'with ' not in company.lower():
                        # Skip known non-employee collaborations
                        # (Alessandro Pasotti is QCooperative, not North Road employee)
                        if dev_name == "Alessandro Pasotti" and "North Road" in company:
                            continue
                        
                        # Normalize names
                        dev_name = developer_normalizations.get(dev_name, dev_name)
                        normalized_company = normalize_company_name(company)
                        company_developers[normalized_company].add(dev_name)
                        company_developer_features[(normalized_company, dev_name)] += 1
        
        print(f"✅ Processed {INPUT_CSV}")
        
    except FileNotFoundError:
        print(f"❌ File {INPUT_CSV} not found!")
        print(f"   Please run 'python3 scripts/extract_raw_features.py' first.")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Save to CSV
    print(f"\n💾 Saving to CSV: {OUTPUT_CSV}")
    
    csv_data = []
    for company in sorted(company_developers.keys()):
        developers = sorted(company_developers[company])
        for developer in developers:
            feature_count = company_developer_features[(company, developer)]
            csv_data.append({
                'company': company,
                'developer': developer,
                'feature_count': feature_count
            })
    
    try:
        with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['company', 'developer', 'feature_count'])
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"✅ CSV saved: {OUTPUT_CSV}")
    except Exception as e:
        print(f"⚠️  Could not save CSV: {e}")
    
    # Save to text file for readable format
    output_lines = []
    header = "=" * 70
    title = "AZIENDE E SVILUPPATORI ASSOCIATI"
    
    output_lines.append(header)
    output_lines.append(title)
    output_lines.append(header)
    output_lines.append("")
    
    print("\n" + header)
    print(title)
    print(header)
    print()
    
    # Sort companies by number of developers (descending)
    sorted_companies = sorted(
        company_developers.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    for company, developers in sorted_companies:
        developers_list = sorted(developers)
        if developers_list:
            # Count total features for this company
            total_features = sum(company_developer_features[(company, dev)] for dev in developers_list)
            
            company_line = f"🏢 {company} ({len(developers_list)} sviluppatori, {total_features} features)"
            output_lines.append(company_line)
            print(company_line)
            
            for developer in developers_list:
                feature_count = company_developer_features[(company, developer)]
                dev_line = f"   👤 {developer} ({feature_count} features)"
                output_lines.append(dev_line)
                print(dev_line)
            
            output_lines.append("")
            print()
    
    footer = f"Totale aziende identificate: {len(company_developers)}"
    output_lines.append(header)
    output_lines.append(footer)
    output_lines.append(header)
    
    print(header)
    print(footer)
    print(header)
    
    # Save to text file
    try:
        with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"\n💾 Results saved to: {OUTPUT_TXT}")
    except Exception as e:
        print(f"\n⚠️  Could not save text file: {e}")
    
    # Additional statistics
    print("\n" + "=" * 70)
    print("STATISTICHE TOP 20 AZIENDE PER NUMERO DI SVILUPPATORI")
    print("=" * 70)
    
    top_companies = sorted(
        company_developers.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:20]
    
    for company, developers in top_companies:
        total_features = sum(company_developer_features[(company, dev)] for dev in developers)
        print(f"   {len(developers):2d} sviluppatori, {total_features:4d} features: {company}")
    
    print("=" * 70)

if __name__ == "__main__":
    print("🚀 Starting companies and developers extraction")
    print("=" * 70)
    extract_companies_developers()
    print("\n🎉 Process completed!")
