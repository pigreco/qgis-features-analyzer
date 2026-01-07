#!/usr/bin/env python3
"""
Script to extract raw information from QGIS changelog ZIP files.
Reads .md files inside the ZIPs and extracts raw data without normalization:
- Feature name
- Category
- Developer
- Funder
"""

import os
import zipfile
import re
from pathlib import Path
import csv

DOWNLOAD_DIR = "data/qgis_downloads"
OUTPUT_CSV = "output/qgis_features_raw.csv"

def extract_md_from_zip(zip_path):
    """Extract the content of .md files from a ZIP archive"""
    md_contents = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find all .md files in the archive
            md_files = [f for f in zip_ref.namelist() if f.endswith('.md')]
            
            for md_file in md_files:
                content = zip_ref.read(md_file).decode('utf-8', errors='ignore')
                md_contents.append({
                    'filename': md_file,
                    'content': content
                })
                
    except Exception as e:
        print(f"   ❌ Error opening {zip_path}: {e}")
        return []
    
    return md_contents



def extract_links_from_markdown(text):
    """
    Extract markdown links [text](url) and return a list of URLs.
    """
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', text)
    # Return only URLs (second element of each tuple)
    return [url for _, url in links] if links else []

def clean_markdown_links(text):
    """Remove markdown links [text](url) leaving only the text"""
    # Pattern for [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove remaining square brackets
    text = text.replace('[', '').replace(']', '')
    # Clean multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_developer_info_raw(text, lines, start_idx):
    """
    Extract developer information handling multiline cases.
    Returns a tuple (cleaned_name, link)
    NO NORMALIZATION - keeps original text
    """
    # Clean initial text
    developer = text.strip()
    
    # If text seems incomplete (ends with comma or very short),
    # check next line as well
    if start_idx + 1 < len(lines):
        next_line = lines[start_idx + 1].strip()
        # If next line doesn't start with markdown pattern (###, ##, #####)
        # and is not empty, it might be the continuation
        if next_line and not next_line.startswith('#') and not next_line.startswith('*'):
            # If current developer ends with comma or seems truncated
            if developer.endswith(',') or len(developer) < 5:
                developer += ' ' + next_line
    
    # Extract links before cleaning text
    links = extract_links_from_markdown(developer)
    developer_link = links[0] if links else ""
    
    # Clean result
    developer = clean_markdown_links(developer)
    
    # Remove residual special characters at beginning
    developer = re.sub(r'^[\[\]\(\)\{\}]+', '', developer)
    
    # Remove end patterns like "This feature was"
    developer = re.sub(r'This feature was.*$', '', developer, flags=re.IGNORECASE)
    
    # Basic cleanup only - NO normalization
    developer = developer.strip()
    developer = re.sub(r'\s+', ' ', developer)
    
    # If empty after cleanup, return "Not specified"
    if not developer or developer == '':
        return 'Not specified', developer_link
    
    return developer, developer_link

def extract_funder_info_raw(text, lines, start_idx):
    """
    Extract funder information handling multiline cases.
    Returns a tuple (cleaned_name, link)
    NO NORMALIZATION - keeps original text
    """
    # Clean initial text
    funder = text.strip()
    
    # If text seems incomplete, check next line as well
    if start_idx + 1 < len(lines):
        next_line = lines[start_idx + 1].strip()
        if next_line and not next_line.startswith('#') and not next_line.startswith('*'):
            if funder.endswith(',') or len(funder) < 5:
                funder += ' ' + next_line
    
    # Extract links before cleaning text
    links = extract_links_from_markdown(funder)
    funder_link = links[0] if links else ""
    
    # Clean result
    funder = clean_markdown_links(funder)
    
    # Remove residual special characters at beginning
    funder = re.sub(r'^[\[\]\(\)\{\}]+', '', funder)
    
    # Remove end patterns
    funder = re.sub(r'This feature was.*$', '', funder, flags=re.IGNORECASE)
    
    # Basic cleanup only - NO normalization
    funder = funder.strip()
    funder = re.sub(r'\s+', ' ', funder)
    
    # If empty after cleanup, return "Not specified"
    if not funder or funder == '':
        return 'Not specified', funder_link
    
    return funder, funder_link

def parse_feature_info(content):
    """
    Parse markdown content to extract feature information.
    Typical format is:
    
    ## Category
    
    ### Feature: Feature name
    
    Description...
    
    ##### This feature was funded by Funder
    ##### This feature was developed by Developer
    """
    features = []
    
    # Patterns to identify sections
    category_pattern = r'^##\s+(.+?)$'
    feature_pattern = r'^###\s+Feature:\s*(.+?)$'
    # Updated patterns to handle multiline cases
    funded_pattern = r'(?:This feature was funded by|Funded by)\s+(.+?)(?=\n\n|\n###|\n##|$)'
    developed_pattern = r'(?:This feature was developed by|Developed by)\s+(.+?)(?=\n\n|\n###|\n##|$)'
    
    lines = content.split('\n')
    current_category = "Unknown"
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if it's a category
        cat_match = re.match(category_pattern, line)
        if cat_match:
            current_category = cat_match.group(1).strip()
            i += 1
            continue
        
        # Check if it's a feature
        feat_match = re.match(feature_pattern, line)
        if feat_match:
            feature_name = feat_match.group(1).strip()
            
            # Search for funding and development info in following lines
            # Typically within the next 50 lines
            funded_by = "Not specified"
            funded_by_link = ""
            developed_by = "Not specified"
            developed_by_link = ""
            
            # Collect following text until next feature or category
            following_text = ""
            for j in range(i + 1, min(i + 100, len(lines))):
                next_line = lines[j]
                
                # Stop if encountering a new feature or category
                if re.match(r'^###\s+Feature:', next_line) or re.match(r'^##\s+', next_line):
                    break
                
                following_text += next_line + "\n"
            
            # Search in the collected text (handles multiline cases)
            funded_match = re.search(funded_pattern, following_text, re.IGNORECASE | re.DOTALL)
            if funded_match:
                # Replace newlines with spaces in the matched text
                matched_text = funded_match.group(1).replace('\n', ' ')
                funded_by, funded_by_link = extract_funder_info_raw(matched_text, [matched_text], 0)
                if not funded_by or funded_by.strip() == '':
                    funded_by = "Not specified"
            
            # Search for developed by
            developed_match = re.search(developed_pattern, following_text, re.IGNORECASE | re.DOTALL)
            if developed_match:
                # Replace newlines with spaces in the matched text
                matched_text = developed_match.group(1).replace('\n', ' ')
                developed_by, developed_by_link = extract_developer_info_raw(matched_text, [matched_text], 0)
                if not developed_by or developed_by.strip() == '':
                    developed_by = "Not specified"
            
            features.append({
                'category': current_category,
                'feature_name': feature_name,
                'funded_by': funded_by if funded_by else "Not specified",
                'funded_by_link': funded_by_link,
                'developed_by': developed_by if developed_by else "Not specified",
                'developed_by_link': developed_by_link
            })
        
        i += 1
    
    return features

def process_all_zips():
    """Process all ZIP files in the download directory"""
    
    if not os.path.exists(DOWNLOAD_DIR):
        print(f"❌ Directory {DOWNLOAD_DIR} not found!")
        return
    
    all_features = []
    zip_files = sorted([f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.zip')])
    
    if not zip_files:
        print(f"❌ No ZIP files found in {DOWNLOAD_DIR}")
        return
    
    print(f"🔍 Found {len(zip_files)} ZIP files to analyze")
    print("=" * 70)
    
    for zip_filename in zip_files:
        zip_path = os.path.join(DOWNLOAD_DIR, zip_filename)
        
        # Extract version name from filename
        version = zip_filename.replace('qgis_', '').replace('_changelog.zip', '')
        
        print(f"\n📦 Processing: {zip_filename}")
        print(f"   Version: {version}")
        
        # Extract .md files
        md_contents = extract_md_from_zip(zip_path)
        
        if not md_contents:
            print(f"   ⚠️  No .md files found")
            continue
        
        print(f"   📄 Found {len(md_contents)} .md file(s)")
        
        # Parse each .md file
        features_count = 0
        for md_info in md_contents:
            # Extract features
            features = parse_feature_info(md_info['content'])
            
            # Add version and file information
            for feature in features:
                feature['version'] = version
                feature['md_file'] = md_info['filename']
                all_features.append(feature)
                features_count += 1
        
        print(f"   ✅ Extracted {features_count} features")
    
    return all_features

def save_to_csv(features, output_file):
    """Save extracted features to a CSV file"""
    
    if not features:
        print("\n⚠️  No features to save")
        return
    
    print(f"\n💾 Saving results to {output_file}...")
    
    # Define columns
    fieldnames = ['version', 'category', 'feature_name', 
                  'funded_by', 'funded_by_link', 'developed_by', 'developed_by_link', 'md_file']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(features)
    
    print(f"✅ Saved {len(features)} features to CSV file")

def print_statistics(features):
    """Print statistics about extracted features"""
    
    if not features:
        return
    
    print("\n" + "=" * 70)
    print("📊 STATISTICS")
    print("=" * 70)
    
    # Count by version
    versions = {}
    for f in features:
        v = f['version']
        versions[v] = versions.get(v, 0) + 1
    
    print(f"\n📈 Features by version:")
    for version in sorted(versions.keys(), reverse=True):
        print(f"   {version}: {versions[version]} features")
    
    # Count by category
    categories = {}
    for f in features:
        c = f['category']
        categories[c] = categories.get(c, 0) + 1
    
    print(f"\n📂 Top 10 categories:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {category}: {count} features")
    
    # Count specified vs unspecified
    specified_dev = sum(1 for f in features if f['developed_by'] != 'Not specified')
    specified_fund = sum(1 for f in features if f['funded_by'] != 'Not specified')
    
    print(f"\n📋 Data completeness:")
    print(f"   Developers specified: {specified_dev}/{len(features)} ({100*specified_dev/len(features):.1f}%)")
    print(f"   Funders specified: {specified_fund}/{len(features)} ({100*specified_fund/len(features):.1f}%)")

def main():
    """Main function"""
    print("🚀 Starting RAW data extraction from QGIS changelogs")
    print("   (No normalization applied)")
    print("=" * 70)
    
    # Process all ZIP files
    features = process_all_zips()
    
    if features:
        # Save to CSV
        save_to_csv(features, OUTPUT_CSV)
        
        # Show statistics
        print_statistics(features)
        
        print(f"\n📁 CSV file saved: {os.path.abspath(OUTPUT_CSV)}")
    
    print("\n🎉 Process completed!")

if __name__ == "__main__":
    main()
