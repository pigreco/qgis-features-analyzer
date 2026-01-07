#!/usr/bin/env python3
"""
Script per scaricare gli archivi ZIP dalle pagine di changelog di QGIS
Versioni: dalla 3.0 alla 3.44
"""

import os
import requests
from pathlib import Path

DOWNLOAD_DIR = "qgis_downloads"
URLS_FILE = "changelog_urls.txt"

def load_changelog_urls(filename):
    """Carica gli URL dal file di configurazione"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Ignora righe vuote e commenti
                if line and not line.startswith('#'):
                    urls.append(line)
        print(f"📋 Caricate {len(urls)} URL da {filename}")
        return urls
    except FileNotFoundError:
        print(f"❌ Errore: File {filename} non trovato!")
        return []
    except Exception as e:
        print(f"❌ Errore nella lettura del file {filename}: {e}")
        return []

def extract_version_from_url(url):
    """Estrae la versione dall'URL per il nome del file"""
    # Estrai la parte tra /version/ e /md/
    version_part = url.split('/version/')[1].split('/md/')[0]
    return version_part

def create_download_directory():
    """Crea la directory per i download se non esiste"""
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
    print(f"📁 Directory di download: {DOWNLOAD_DIR}")

def check_url_exists(url):
    """Verifica se l'URL esiste ed è accessibile"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False

def download_file(url, destination):
    """Scarica un file da URL verso la destinazione specificata"""
    try:
        print(f"  ⬇️  Scaricamento: {os.path.basename(destination)}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Scarica con progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        size_mb = os.path.getsize(destination) / (1024 * 1024)
        print(f"  ✅ Completato: {os.path.basename(destination)} ({size_mb:.2f} MB)")
        return True
        
    except requests.RequestException as e:
        print(f"  ❌ Errore durante il download di {url}: {e}")
        return False

def main():
    """Funzione principale"""
    print("🚀 Avvio download degli archivi ZIP di QGIS")
    print("=" * 60)
    
    # Carica gli URL dal file
    changelog_urls = load_changelog_urls(URLS_FILE)
    
    if not changelog_urls:
        print("❌ Nessun URL da processare. Verifica il file changelog_urls.txt")
        return
    
    create_download_directory()
    
    total_attempts = 0
    successful_downloads = 0
    skipped = 0
    
    for url in changelog_urls:
        version_str = extract_version_from_url(url)
        
        print(f"\n📋 Versione {version_str}")
        print(f"   URL: {url}")
        
        # Nome del file basato sulla versione
        filename = f"qgis_{version_str}_changelog.zip"
        destination = os.path.join(DOWNLOAD_DIR, filename)
        
        # Salta se il file esiste già
        if os.path.exists(destination):
            file_size = os.path.getsize(destination) / (1024 * 1024)
            print(f"   ⏭️  File già esistente: {filename} ({file_size:.2f} MB)")
            skipped += 1
            continue
        
        # Verifica se l'URL esiste
        if not check_url_exists(url):
            print(f"   ❌ URL non trovato o non accessibile")
            continue
        
        total_attempts += 1
        print(f"   ⬇️  Scaricamento in corso...")
        
        if download_file(url, destination):
            successful_downloads += 1
    
    # Riepilogo finale
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO")
    print("=" * 60)
    print(f"⏭️  File già esistenti: {skipped}")
    print(f"⬇️  Nuovi download tentati: {total_attempts}")
    print(f"✅ Download completati con successo: {successful_downloads}")
    if total_attempts > 0:
        print(f"📈 Tasso di successo: {(successful_downloads/total_attempts)*100:.1f}%")
    print(f"📁 Posizione file: {os.path.abspath(DOWNLOAD_DIR)}")
    print("\n🎉 Processo completato!")

if __name__ == "__main__":
    main()