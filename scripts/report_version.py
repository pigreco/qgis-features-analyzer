#!/usr/bin/env python3
"""
Genera un report riepilogativo per una singola versione di QGIS a partire
dai dati gia' normalizzati dalla pipeline (output/qgis_features_normalized_dev.csv).

Uso:
    python3 scripts/report_version.py [VERSIONE]

Se la versione non e' indicata, usa 4.2.
Produce un file Markdown in output/qgis_<versione>_summary.md

Generate a summary report for a single QGIS version using the already
normalized pipeline data. Outputs a Markdown file in output/.
"""

import sys
import csv
from collections import Counter, defaultdict

NORMALIZED_CSV = "output/qgis_features_normalized_dev.csv"
COMPANIES_CSV = "output/companies_developers.csv"


def load_features(version):
    """Carica le feature della versione richiesta dal CSV normalizzato."""
    rows = []
    with open(NORMALIZED_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["version"] == version:
                rows.append(r)
    return rows


def load_company_of_developer():
    """
    Mappa sviluppatore -> azienda principale.
    Uno sviluppatore puo' comparire con piu' aziende (es. co-sviluppo):
    si sceglie l'azienda con il maggior numero di feature attribuite.
    """
    best = {}  # developer -> (feature_count, company)
    try:
        with open(COMPANIES_CSV, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                dev = r["developer"]
                count = int(r.get("feature_count", 0) or 0)
                if dev not in best or count > best[dev][0]:
                    best[dev] = (count, r["company"])
    except FileNotFoundError:
        pass
    return {dev: co for dev, (cnt, co) in best.items()}


def bar(n, maxn, width=24):
    """Piccola barra ASCII proporzionale."""
    filled = int(round(width * n / maxn)) if maxn else 0
    return "█" * filled + "·" * (width - filled)


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "4.2"
    feats = load_features(version)

    if not feats:
        print(f"❌ Nessuna feature trovata per la versione {version} in {NORMALIZED_CSV}")
        print("   Esegui prima: extract_raw_features.py -> normalize_developers.py")
        sys.exit(1)

    dev2co = load_company_of_developer()

    total = len(feats)
    cats = Counter(f["category"] for f in feats)
    devs = Counter(f["developed_by"] for f in feats if f["developed_by"] != "Not specified")
    funds = Counter(f["funded_by"] for f in feats if f["funded_by"] != "Not specified")

    spec_dev = sum(1 for f in feats if f["developed_by"] != "Not specified")
    spec_fund = sum(1 for f in feats if f["funded_by"] != "Not specified")

    # Aggregazione per azienda (via mappatura sviluppatore->azienda)
    company_feats = Counter()
    for f in feats:
        co = dev2co.get(f["developed_by"])
        if co:
            company_feats[co] += 1

    out_path = f"output/qgis_{version}_summary.md"
    L = []
    L.append(f"# Report QGIS {version}")
    L.append("")
    L.append(f"Riepilogo generato dal changelog QGIS {version}.")
    L.append("")
    L.append("## Panoramica")
    L.append("")
    L.append(f"- **Feature totali:** {total}")
    L.append(f"- **Categorie:** {len(cats)}")
    L.append(f"- **Sviluppatori distinti:** {len(devs)}")
    L.append(f"- **Finanziatori distinti:** {len(funds)}")
    L.append(f"- **Feature con sviluppatore indicato:** {spec_dev}/{total} ({100*spec_dev/total:.0f}%)")
    L.append(f"- **Feature con finanziatore indicato:** {spec_fund}/{total} ({100*spec_fund/total:.0f}%)")
    L.append("")

    L.append("## Feature per categoria")
    L.append("")
    L.append("| Categoria | Feature | |")
    L.append("|---|--:|:--|")
    maxc = cats.most_common(1)[0][1]
    for c, n in cats.most_common():
        L.append(f"| {c} | {n} | `{bar(n, maxc)}` |")
    L.append("")

    L.append("## Top sviluppatori")
    L.append("")
    L.append("| # | Sviluppatore | Feature | Azienda |")
    L.append("|--:|---|--:|---|")
    for i, (d, n) in enumerate(devs.most_common(15), 1):
        co = dev2co.get(d, "—")
        L.append(f"| {i} | {d} | {n} | {co} |")
    L.append("")

    if company_feats:
        L.append("## Feature per azienda (via mappatura sviluppatori)")
        L.append("")
        L.append("| Azienda | Feature |")
        L.append("|---|--:|")
        for co, n in company_feats.most_common():
            L.append(f"| {co} | {n} |")
        L.append("")

    L.append("## Finanziatori")
    L.append("")
    if funds:
        L.append("| Finanziatore | Feature |")
        L.append("|---|--:|")
        for fn, n in funds.most_common():
            L.append(f"| {fn} | {n} |")
    else:
        L.append("Nessun finanziatore indicato.")
    L.append("")

    L.append("## Elenco completo delle feature")
    L.append("")
    by_cat = defaultdict(list)
    for f in feats:
        by_cat[f["category"]].append(f)
    for c, _ in cats.most_common():
        L.append(f"### {c}")
        L.append("")
        for f in by_cat[c]:
            dev = f["developed_by"]
            fund = f["funded_by"]
            extra = f" — dev: *{dev}*" if dev != "Not specified" else ""
            if fund != "Not specified":
                extra += f" · fondi: *{fund}*"
            L.append(f"- **{f['feature_name']}**{extra}")
        L.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print(f"✅ Report salvato: {out_path}")
    print(f"   {total} feature · {len(cats)} categorie · {len(devs)} sviluppatori · {len(funds)} finanziatori")


if __name__ == "__main__":
    main()
