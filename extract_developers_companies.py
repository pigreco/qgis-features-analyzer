#!/usr/bin/env python3
"""
Script to extract developers and their associated companies from QGIS features CSV.
Analyzes the developed_by and funded_by fields to create a mapping of developers to companies.
"""

import csv
import re
from collections import defaultdict

INPUT_CSV = "qgis_features_raw.csv"
OUTPUT_TXT = "developers_companies.txt"

def extract_developers_and_companies():
    """Extract and map developers to their associated companies"""
    
    # Dictionary to map developers to companies
    developer_companies = defaultdict(set)
    
    print("🔍 Reading CSV file...")
    
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                developer = row['developed_by'].strip()
                
                if not developer or developer == 'Not specified':
                    continue
                
                # Pattern to extract name and company from "Name (Company)"
                match = re.search(r'^(.+?)\s*\(([^)]+)\)$', developer)
                
                if match:
                    name = match.group(1).strip()
                    company = match.group(2).strip()
                    
                    # Clean quotes from name
                    name = name.strip('"')
                    
                    # Ignore if company is a URL
                    if not company.startswith('http'):
                        developer_companies[name].add(company)
                else:
                    # If no parenthesis, check if there's info in the funder field
                    funder = row['funded_by'].strip()
                    if funder and funder != 'Not specified' and developer != 'Not specified':
                        # Clean quotes from developer name
                        developer = developer.strip('"')
                        # Only if developer doesn't contain organization keywords
                        if not any(org in developer.lower() for org in ['kartoza', 'north road', 'oslandia', 'opengis', 'lutra', 'faunalia']):
                            if not funder.startswith('http') and len(funder) < 50:
                                developer_companies[developer].add(funder)
        
        print(f"✅ Processed {INPUT_CSV}")
        
    except FileNotFoundError:
        print(f"❌ File {INPUT_CSV} not found!")
        print(f"   Please run 'python3 extract_raw_features.py' first.")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Print results to console and save to file
    output_lines = []
    
    header = "=" * 70
    title = "SVILUPPATORI E AZIENDE ASSOCIATE"
    
    output_lines.append(header)
    output_lines.append(title)
    output_lines.append(header)
    output_lines.append("")
    
    print("\n" + header)
    print(title)
    print(header)
    print()
    
    # Sort developers and their companies
    for developer in sorted(developer_companies.keys()):
        companies = sorted(developer_companies[developer])
        if companies:
            dev_line = f"👤 {developer}"
            output_lines.append(dev_line)
            print(dev_line)
            
            for company in companies:
                comp_line = f"   🏢 {company}"
                output_lines.append(comp_line)
                print(comp_line)
            
            output_lines.append("")
            print()
    
    footer = f"Totale sviluppatori identificati: {len(developer_companies)}"
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
        print(f"\n⚠️  Could not save to file: {e}")
    
    # Additional statistics
    print("\n" + "=" * 70)
    print("STATISTICHE AZIENDE PIÙ FREQUENTI")
    print("=" * 70)
    
    # Count companies occurrences
    company_counts = defaultdict(int)
    for companies in developer_companies.values():
        for company in companies:
            company_counts[company] += 1
    
    # Print top 20 companies
    top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    for company, count in top_companies:
        print(f"   {count:3d} sviluppatori: {company}")
    
    print("=" * 70)

if __name__ == "__main__":
    print("🚀 Starting developers and companies extraction")
    print("=" * 70)
    extract_developers_and_companies()
    print("\n🎉 Process completed!")
