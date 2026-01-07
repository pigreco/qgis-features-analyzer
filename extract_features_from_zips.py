#!/usr/bin/env python3
"""
Script per estrarre informazioni dai file ZIP dei changelog di QGIS
Legge i file .md all'interno degli ZIP ed estrae:
- Nome della feature
- Categoria
- Developer
- Finanziatore
"""

import os
import zipfile
import re
from pathlib import Path
import csv

DOWNLOAD_DIR = "qgis_downloads"
OUTPUT_CSV = "qgis_features_extracted.csv"

def extract_md_from_zip(zip_path):
    """Estrae il contenuto dei file .md da un archivio ZIP"""
    md_contents = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Trova tutti i file .md nell'archivio
            md_files = [f for f in zip_ref.namelist() if f.endswith('.md')]
            
            for md_file in md_files:
                content = zip_ref.read(md_file).decode('utf-8', errors='ignore')
                md_contents.append({
                    'filename': md_file,
                    'content': content
                })
                
    except Exception as e:
        print(f"   ❌ Errore nell'apertura di {zip_path}: {e}")
        return []
    
    return md_contents

def extract_metadata(content):
    """
    Estrae metadati della versione come data di rilascio e nome della versione.
    Cerca pattern come:
    - Release date: 23 February, 2018
    - # Changelog for QGIS 3.0.0
    """
    metadata = {
        'release_date': 'Not specified',
        'version_name': 'Not specified'
    }
    
    # Pattern per la data di rilascio
    date_pattern = r'(?:Release date|Released):\s*(.+?)(?:\n|$)'
    date_match = re.search(date_pattern, content, re.IGNORECASE)
    if date_match:
        metadata['release_date'] = date_match.group(1).strip()
    
    # Pattern per il nome della versione nel titolo
    # Es: "# Changelog for QGIS 3.0.0" o "QGIS 3.10 'A Coruña'"
    version_name_patterns = [
        r'#\s+Changelog for QGIS\s+([\d.]+(?:-LTR)?)\s*[\'"]?([^\'"#\n]*)[\'"]?',
        r'QGIS\s+([\d.]+(?:-LTR)?)\s+[\'"]([^\'"]+)[\'"]',
        r'(?:Introducing|Announcing|Release of)\s+QGIS\s+([\d.]+(?:-LTR)?)\s*[,\s]+([^\n,]+)',
    ]
    
    for pattern in version_name_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            version_num = match.group(1).strip()
            if len(match.groups()) > 1:
                version_label = match.group(2).strip()
                if version_label and not version_label.startswith('a '):
                    metadata['version_name'] = f"{version_num} '{version_label}'"
                else:
                    metadata['version_name'] = version_num
            else:
                metadata['version_name'] = version_num
            break
    
    return metadata

def parse_feature_info(content, metadata):
    """
    Analizza il contenuto markdown per estrarre informazioni sulle feature.
    Il formato tipico è:
    
    ## Categoria
    
    ### Feature: Nome della feature
    
    Descrizione...
    
    ##### This feature was funded by Finanziatore
    ##### This feature was developed by Developer
    """
    features = []
    
    # Pattern per identificare le sezioni
    # Cerca pattern tipo "## Categoria" seguito da "### Feature: Nome"
    category_pattern = r'^##\s+(.+?)$'
    feature_pattern = r'^###\s+Feature:\s*(.+?)$'
    funded_pattern = r'(?:This feature was funded by|Funded by)\s+(.+?)(?:\n|$)'
    developed_pattern = r'(?:This feature was developed by|Developed by)\s+(.+?)(?:\n|$)'
    
    lines = content.split('\n')
    current_category = "Unknown"
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Verifica se è una categoria
        cat_match = re.match(category_pattern, line)
        if cat_match:
            current_category = cat_match.group(1).strip()
            i += 1
            continue
        
        # Verifica se è una feature
        feat_match = re.match(feature_pattern, line)
        if feat_match:
            feature_name = feat_match.group(1).strip()
            
            # Cerca le informazioni di funding e development nelle righe successive
            # Tipicamente sono entro le prossime 50 righe
            funded_by = "Not specified"
            funded_by_link = ""
            developed_by = "Not specified"
            developed_by_link = ""
            
            for j in range(i + 1, min(i + 100, len(lines))):
                next_line = lines[j]
                
                # Ferma se incontri una nuova feature o categoria
                if re.match(r'^###\s+Feature:', next_line) or re.match(r'^##\s+', next_line):
                    break
                
                # Cerca funded by
                funded_match = re.search(funded_pattern, next_line, re.IGNORECASE)
                if funded_match and funded_by == "Not specified":
                    funded_by, funded_by_link = extract_funder_info(funded_match.group(1), lines, j)
                    # Verifica se il risultato è vuoto
                    if not funded_by or funded_by.strip() == '':
                        funded_by = "Not specified"
                
                # Cerca developed by
                developed_match = re.search(developed_pattern, next_line, re.IGNORECASE)
                if developed_match and developed_by == "Not specified":
                    developed_by, developed_by_link = extract_developer_info(developed_match.group(1), lines, j)
                    # Verifica se il risultato è vuoto
                    if not developed_by or developed_by.strip() == '':
                        developed_by = "Not specified"
            
            features.append({
                'category': current_category,
                'feature_name': feature_name,
                'funded_by': funded_by if funded_by else "Not specified",
                'funded_by_link': funded_by_link,
                'developed_by': developed_by if developed_by else "Not specified",
                'developed_by_link': developed_by_link,
                'release_date': metadata['release_date'],
                'version_name': metadata['version_name']
            })
        
        i += 1
    
    return features

def extract_links_from_markdown(text):
    """
    Estrae i link markdown [testo](url) e restituisce una lista di URL.
    """
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', text)
    # Restituisce solo gli URL (secondo elemento di ogni tupla)
    return [url for _, url in links] if links else []

def clean_markdown_links(text):
    """Rimuove i link markdown [testo](url) lasciando solo il testo"""
    # Pattern per [testo](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Rimuove eventuali tag HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Rimuove parentesi quadre residue
    text = text.replace('[', '').replace(']', '')
    # Pulisce spazi multipli
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_developer_name(name):
    """
    Normalizza i nomi dei developer secondo le regole specificate:
    1. Nyall o Nyall Dawson → Nyall Dawson
    2. Mathieu o Mathieu Pellerin → Mathieu Pellerin
    3. Alessandro → Alessandro Pasotti
    4. Alexander o Alex Bruy → Alexander Bruy
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
    21. Matteo Ghetta (inizia con) → Matteo Ghetta
    22. Marco → Marco Bernasocchi
    23. Tutti i nomi con "Lutra" → Lutra Consulting
    24. Tutti i nomi con "OPENGIS.ch" → OPENGIS.ch
    25. Tutti i nomi con "Kartoza" → Kartoza
    26. Nomi vuoti → Not specified
    27. Rimuove (North Road), (North), (Lutra Consulting), (Lutra), etc.
    28. Rimuove ' /' finale
    """
    if not name or name == "Not specified":
        return name
    
    original_name = name
    
    # Prima di tutto, controlla se c'è OPENGIS.ch nel nome (prima di rimuoverlo)
    if 'opengis.ch' in name.lower() or 'opengis' in name.lower():
        return 'OPENGIS.ch'
    
    # Kartoza (qualsiasi nome con Kartoza) → Kartoza
    if 'kartoza' in name.lower():
        return 'Kartoza'
    
    # Rimuove riferimenti a aziende tra parentesi PRIMA della normalizzazione
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
    
    # Rimuove "OSLANDIA - " prefix
    name = re.sub(r'^OSLANDIA\s*-\s*', '', name, flags=re.IGNORECASE)
    
    # Rimuove "in collaboration with" e simili
    name = re.sub(r'\s+in collaboration with.*$', '', name, flags=re.IGNORECASE)
    
    # Normalizza nomi specifici
    name = name.strip()
    
    # Se il nome è vuoto dopo la pulizia, ritorna "Not specified"
    if not name or name == '':
        return 'Not specified'
    
    name_lower = name.lower()
    
    # North Road (solo) → Nyall Dawson
    if name_lower == 'north road':
        return 'Nyall Dawson'
    
    # jef-n → Jürgen Fischer
    if 'jef-n' in name_lower or name_lower == 'jef-n':
        return 'Jürgen Fischer'
    
    # Juergen E. Fischer o Jürgen Fischer → Jürgen Fischer
    if 'juergen' in name_lower or 'jürgen' in name_lower:
        return 'Jürgen Fischer'
    
    # Lutra (qualsiasi nome con Lutra) → Lutra Consulting
    if 'lutra' in name_lower:
        return 'Lutra Consulting'
    
    # Denis (inizia con Denis) → Denis Rouzaud
    if name_lower.startswith('denis'):
        return 'Denis Rouzaud'
    
    # Etienne/Étienne → Étienne Trimaille
    if name_lower.startswith('etienne') or name_lower.startswith('étienne'):
        return 'Étienne Trimaille'
    
    # Matteo Ghetta (inizia con) → Matteo Ghetta
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
    
    # Alexander Bruy (gestisce anche Alex Bruy)
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
    
    # Paul Blottiere (gestisce Paul, Pau Blottiere, OSLANDIA - Paul)
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
    
    # Pulisce spazi multipli e virgole finali
    name = re.sub(r'\s+', ' ', name).strip()
    name = name.rstrip(',').strip()
    
    # Rimuove ' /' finale
    name = re.sub(r'\s*/\s*$', '', name).strip()
    
    # Controllo finale: se dopo tutte le pulizie il nome è vuoto
    if not name or name == '':
        return 'Not specified'
    
    return name

def extract_developer_info(text, lines, start_idx):
    """
    Estrae informazioni sul developer gestendo meglio i casi multiriga.
    Restituisce una tupla (nome_pulito, link)
    """
    # Pulisci il testo iniziale
    developer = text.strip()
    
    # Se il testo sembra incompleto (termina con una virgola o è molto corto),
    # guarda anche la riga successiva
    if start_idx + 1 < len(lines):
        next_line = lines[start_idx + 1].strip()
        # Se la riga successiva non inizia con un pattern markdown (###, ##, #####)
        # e non è vuota, potrebbe essere la continuazione
        if next_line and not next_line.startswith('#') and not next_line.startswith('*'):
            # Se il developer corrente termina con virgola o sembra troncato
            if developer.endswith(',') or len(developer) < 5:
                developer += ' ' + next_line
    
    # Estrai i link prima di pulire il testo
    links = extract_links_from_markdown(developer)
    developer_link = links[0] if links else ""
    
    # Pulisci il risultato
    developer = clean_markdown_links(developer)
    
    # Rimuovi caratteri speciali residui all'inizio
    developer = re.sub(r'^[\[\]\(\)\{\}]+', '', developer)
    
    # Rimuovi eventuali pattern di fine come "This feature was"
    developer = re.sub(r'This feature was.*$', '', developer, flags=re.IGNORECASE)
    
    # Normalizza il nome
    developer = normalize_developer_name(developer.strip())
    
    return developer, developer_link

def extract_funder_info(text, lines, start_idx):
    """
    Estrae informazioni sul finanziatore gestendo meglio i casi multiriga.
    Restituisce una tupla (nome_pulito, link)
    """
    # Pulisci il testo iniziale
    funder = text.strip()
    
    # Se il testo sembra incompleto, guarda anche la riga successiva
    if start_idx + 1 < len(lines):
        next_line = lines[start_idx + 1].strip()
        if next_line and not next_line.startswith('#') and not next_line.startswith('*'):
            if funder.endswith(',') or len(funder) < 5:
                funder += ' ' + next_line
    
    # Estrai i link prima di pulire il testo
    links = extract_links_from_markdown(funder)
    funder_link = links[0] if links else ""
    
    # Pulisci il risultato
    funder = clean_markdown_links(funder)
    
    # Rimuovi caratteri speciali residui all'inizio
    funder = re.sub(r'^[\[\]\(\)\{\}]+', '', funder)
    
    # Rimuovi eventuali pattern di fine
    funder = re.sub(r'This feature was.*$', '', funder, flags=re.IGNORECASE)
    
    return funder.strip(), funder_link

def process_all_zips():
    """Processa tutti i file ZIP nella directory di download"""
    
    if not os.path.exists(DOWNLOAD_DIR):
        print(f"❌ Directory {DOWNLOAD_DIR} non trovata!")
        return
    
    all_features = []
    zip_files = sorted([f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.zip')])
    
    if not zip_files:
        print(f"❌ Nessun file ZIP trovato in {DOWNLOAD_DIR}")
        return
    
    print(f"🔍 Trovati {len(zip_files)} file ZIP da analizzare")
    print("=" * 70)
    
    for zip_filename in zip_files:
        zip_path = os.path.join(DOWNLOAD_DIR, zip_filename)
        
        # Estrai il nome della versione dal nome del file
        version = zip_filename.replace('qgis_', '').replace('_changelog.zip', '')
        
        print(f"\n📦 Analisi: {zip_filename}")
        print(f"   Versione: {version}")
        
        # Estrai i file .md
        md_contents = extract_md_from_zip(zip_path)
        
        if not md_contents:
            print(f"   ⚠️  Nessun file .md trovato")
            continue
        
        print(f"   📄 Trovati {len(md_contents)} file .md")
        
        # Analizza ogni file .md
        features_count = 0
        for md_info in md_contents:
            # Estrai metadati (data e nome versione)
            metadata = extract_metadata(md_info['content'])
            
            # Estrai le feature
            features = parse_feature_info(md_info['content'], metadata)
            
            # Aggiungi informazioni sulla versione e file
            for feature in features:
                feature['version'] = version
                feature['md_file'] = md_info['filename']
                all_features.append(feature)
                features_count += 1
        
        print(f"   ✅ Estratte {features_count} feature")
        
        # Mostra i metadati estratti se disponibili
        if all_features and features_count > 0:
            last_feature = all_features[-1]
            if last_feature['version_name'] != 'Not specified':
                print(f"   📌 Nome versione: {last_feature['version_name']}")
            if last_feature['release_date'] != 'Not specified':
                print(f"   📅 Data rilascio: {last_feature['release_date']}")
    
    return all_features

def save_to_csv(features, output_file):
    """Salva le feature estratte in un file CSV"""
    
    if not features:
        print("\n⚠️  Nessuna feature da salvare")
        return
    
    print(f"\n💾 Salvataggio risultati in {output_file}...")
    
    # Definisci le colonne
    fieldnames = ['version', 'version_name', 'release_date', 'category', 'feature_name', 
                  'funded_by', 'funded_by_link', 'developed_by', 'developed_by_link', 'md_file']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(features)
    
    print(f"✅ Salvate {len(features)} feature nel file CSV")

def print_statistics(features):
    """Stampa statistiche sulle feature estratte"""
    
    if not features:
        return
    
    print("\n" + "=" * 70)
    print("📊 STATISTICHE")
    print("=" * 70)
    
    # Conta per versione
    versions = {}
    for f in features:
        v = f['version']
        versions[v] = versions.get(v, 0) + 1
    
    print(f"\n📈 Feature per versione:")
    for version in sorted(versions.keys(), reverse=True):
        print(f"   {version}: {versions[version]} feature")
    
    # Conta per categoria
    categories = {}
    for f in features:
        c = f['category']
        categories[c] = categories.get(c, 0) + 1
    
    print(f"\n📂 Top 10 categorie:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {category}: {count} feature")
    
    # Developer più attivi
    developers = {}
    for f in features:
        d = f['developed_by']
        if d != "Not specified":
            developers[d] = developers.get(d, 0) + 1
    
    print(f"\n👨‍💻 Top 10 developer:")
    for dev, count in sorted(developers.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {dev}: {count} feature")
    
    # Finanziatori più attivi
    funders = {}
    for f in features:
        fund = f['funded_by']
        if fund != "Not specified":
            funders[fund] = funders.get(fund, 0) + 1
    
    print(f"\n💰 Top 10 finanziatori:")
    for funder, count in sorted(funders.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {funder}: {count} feature")

def main():
    """Funzione principale"""
    print("🚀 Avvio estrazione informazioni dai changelog QGIS")
    print("=" * 70)
    
    # Processa tutti i file ZIP
    features = process_all_zips()
    
    if features:
        # Salva in CSV
        save_to_csv(features, OUTPUT_CSV)
        
        # Mostra statistiche
        print_statistics(features)
        
        print(f"\n📁 File CSV salvato: {os.path.abspath(OUTPUT_CSV)}")
    
    print("\n🎉 Processo completato!")

if __name__ == "__main__":
    main()