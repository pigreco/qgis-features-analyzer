#!/usr/bin/env python3
"""
Script to aggregate data from companies_developers.csv by different columns.
Provides various aggregation views of the data.
"""

import csv
from collections import defaultdict

INPUT_CSV = 'output/companies_developers.csv'
OUTPUT_DIR = 'output/'

def aggregate_data():
    """Aggregate data by different columns."""
    
    print("🚀 Starting data aggregation")
    print("=" * 70)
    
    # Load data
    print(f"\n📖 Reading {INPUT_CSV}...")
    
    companies = defaultdict(lambda: {'developers': [], 'total_features': 0})
    all_data = []
    
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company = row['company']
                developer = row['developer']
                features = int(row['feature_count'])
                
                all_data.append((company, developer, features))
                companies[company]['developers'].append((developer, features))
                companies[company]['total_features'] += features
        
        print(f"✅ Loaded {len(all_data)} records from {len(companies)} companies")
        
    except FileNotFoundError:
        print(f"❌ File {INPUT_CSV} not found!")
        return
    
    # 1. Aggregate by Company (sum features)
    print(f"\n💾 Creating aggregation by company...")
    
    company_agg_file = f"{OUTPUT_DIR}companies_aggregated.csv"
    with open(company_agg_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['company', 'total_developers', 'total_features', 'avg_features_per_dev'])
        
        for company in sorted(companies.keys()):
            dev_count = len(companies[company]['developers'])
            total_feat = companies[company]['total_features']
            avg_feat = total_feat / dev_count if dev_count > 0 else 0
            writer.writerow([company, dev_count, total_feat, f"{avg_feat:.2f}"])
    
    print(f"✅ Saved to {company_agg_file}")
    
    # 2. Top developers by features (across all companies)
    print(f"\n💾 Creating top developers ranking...")
    
    developer_totals = defaultdict(lambda: {'companies': set(), 'total_features': 0})
    
    for company, developer, features in all_data:
        developer_totals[developer]['companies'].add(company)
        developer_totals[developer]['total_features'] += features
    
    top_devs_file = f"{OUTPUT_DIR}top_developers.csv"
    with open(top_devs_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['developer', 'total_features', 'companies_count', 'companies'])
        
        # Sort by total features
        sorted_devs = sorted(developer_totals.items(), 
                           key=lambda x: x[1]['total_features'], 
                           reverse=True)
        
        for developer, data in sorted_devs:
            writer.writerow([
                developer, 
                data['total_features'], 
                len(data['companies']),
                ', '.join(sorted(data['companies']))
            ])
    
    print(f"✅ Saved to {top_devs_file}")
    
    # 3. Summary statistics
    print(f"\n💾 Creating summary statistics...")
    
    stats_file = f"{OUTPUT_DIR}aggregation_summary.txt"
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("AGGREGATION SUMMARY STATISTICS\n")
        f.write("=" * 70 + "\n\n")
        
        # Overall stats
        total_companies = len(companies)
        total_developers = len(developer_totals)
        total_features = sum(c['total_features'] for c in companies.values())
        
        f.write("📊 OVERALL STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total companies: {total_companies}\n")
        f.write(f"Total unique developers: {total_developers}\n")
        f.write(f"Total features: {total_features}\n")
        f.write(f"Average features per developer: {total_features/total_developers:.2f}\n")
        f.write(f"Average features per company: {total_features/total_companies:.2f}\n\n")
        
        # Company rankings
        f.write("=" * 70 + "\n")
        f.write("🏢 COMPANIES RANKED BY TOTAL FEATURES\n")
        f.write("=" * 70 + "\n\n")
        
        sorted_companies = sorted(companies.items(), 
                                 key=lambda x: x[1]['total_features'], 
                                 reverse=True)
        
        for i, (company, data) in enumerate(sorted_companies, 1):
            dev_count = len(data['developers'])
            feat_count = data['total_features']
            avg = feat_count / dev_count if dev_count > 0 else 0
            f.write(f"{i:2d}. {company:25s} - {feat_count:4d} features, "
                   f"{dev_count:2d} developers (avg: {avg:6.2f})\n")
        
        # Company rankings by developer count
        f.write("\n" + "=" * 70 + "\n")
        f.write("🏢 COMPANIES RANKED BY DEVELOPER COUNT\n")
        f.write("=" * 70 + "\n\n")
        
        sorted_by_devs = sorted(companies.items(), 
                               key=lambda x: len(x[1]['developers']), 
                               reverse=True)
        
        for i, (company, data) in enumerate(sorted_by_devs, 1):
            dev_count = len(data['developers'])
            feat_count = data['total_features']
            f.write(f"{i:2d}. {company:25s} - {dev_count:2d} developers, "
                   f"{feat_count:4d} features\n")
        
        # Top developers
        f.write("\n" + "=" * 70 + "\n")
        f.write("👨‍💻 TOP 20 DEVELOPERS BY FEATURE COUNT\n")
        f.write("=" * 70 + "\n\n")
        
        sorted_devs = sorted(developer_totals.items(), 
                           key=lambda x: x[1]['total_features'], 
                           reverse=True)
        
        for i, (developer, data) in enumerate(sorted_devs[:20], 1):
            companies_list = ', '.join(sorted(data['companies']))
            f.write(f"{i:2d}. {developer:30s} - {data['total_features']:4d} features "
                   f"({companies_list})\n")
        
        # Multi-company developers
        multi_company = [(dev, data) for dev, data in developer_totals.items() 
                        if len(data['companies']) > 1]
        
        if multi_company:
            f.write("\n" + "=" * 70 + "\n")
            f.write("🔄 DEVELOPERS WORKING WITH MULTIPLE COMPANIES\n")
            f.write("=" * 70 + "\n\n")
            
            sorted_multi = sorted(multi_company, 
                                key=lambda x: (len(x[1]['companies']), x[1]['total_features']), 
                                reverse=True)
            
            for developer, data in sorted_multi:
                companies_list = ', '.join(sorted(data['companies']))
                f.write(f"• {developer:30s} - {len(data['companies'])} companies: "
                       f"{companies_list} ({data['total_features']} features)\n")
    
    print(f"✅ Saved to {stats_file}")
    
    # Console summary
    print("\n" + "=" * 70)
    print("📊 AGGREGATION SUMMARY")
    print("=" * 70)
    print(f"Total companies: {total_companies}")
    print(f"Total unique developers: {total_developers}")
    print(f"Total features: {total_features}")
    print(f"Average features per developer: {total_features/total_developers:.2f}")
    
    print("\n🏆 Top 5 companies by features:")
    for i, (company, data) in enumerate(sorted_companies[:5], 1):
        print(f"  {i}. {company:25s} - {data['total_features']:4d} features "
              f"({len(data['developers'])} developers)")
    
    print("\n🌟 Top 5 developers by features:")
    for i, (developer, data) in enumerate(sorted_devs[:5], 1):
        companies_list = ', '.join(sorted(data['companies']))
        print(f"  {i}. {developer:30s} - {data['total_features']:4d} features ({companies_list})")
    
    if multi_company:
        print(f"\n🔄 Developers working with multiple companies: {len(multi_company)}")
    
    print("\n📁 Files generated:")
    print(f"  • {company_agg_file}")
    print(f"  • {top_devs_file}")
    print(f"  • {stats_file}")
    
    print("\n🎉 Aggregation completed!")

if __name__ == '__main__':
    aggregate_data()
