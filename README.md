# QGIS Features Analyzer

Python tools to extract and analyze QGIS features from changelog archives. Converts release notes into structured CSV data with developer attribution, funding sources, and version metadata.

## 📋 Description

This project provides two Python scripts to automate the extraction and analysis of QGIS features from official changelog pages (versions 3.0 to 3.44):

1. **download_qgis_zips.py** - Downloads ZIP archives containing changelogs in Markdown format
2. **extract_features_from_zips.py** - Extracts structured information from Markdown files and generates a CSV

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/pigreco/qgis-features-analyzer.git
cd qgis-features-analyzer

# Install dependencies
pip install -r requirements.txt
```

## 📦 Dependencies

- `requests` >= 2.31.0
- `beautifulsoup4` >= 4.12.0

## 💻 Usage

### 1. Download changelogs

```bash
python download_qgis_zips.py
```

This script:
- Downloads ZIP archives from official QGIS changelogs (versions 3.0-3.44)
- Saves files to the `qgis_downloads/` directory
- Shows progress status for each version

### 2. Extract features

```bash
python extract_features_from_zips.py
```

This script:
- Reads all ZIP archives in the `qgis_downloads/` directory
- Extracts information from each Markdown file
- Generates a CSV file `qgis_features_extracted.csv` with structured data

## 📊 Output

The generated CSV file contains the following columns:

- **Version** - QGIS version (e.g., 3.44, 3.42, etc.)
- **Release Date** - Version release date
- **Category** - Feature category
- **Feature** - Feature name/description
- **Developer** - Developer who implemented the feature
- **Funder** - Organization/entity that funded the development

## 📁 Project Structure

```
qgis-features-analyzer/
├── download_qgis_zips.py          # Script for downloading changelogs
├── extract_features_from_zips.py  # Script for extracting features
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── LICENSE                        # Project license
├── qgis_downloads/                # Directory with downloaded ZIP files (ignored by git)
└── qgis_features_extracted.csv    # Generated CSV file
```

## 🔧 Configuration

### Supported versions

The script supports the following QGIS versions:
- 3.44, 3.42, 3.40, 3.38, 3.36, 3.34, 3.32, 3.30
- 3.28, 3.26, 3.24, 3.22, 3.20, 3.18, 3.16, 3.14
- 3.12, 3.10, 3.8, 3.6.0, 3.4-LTR, 3.2.0, 3.0.0

To add new versions, modify the `CHANGELOG_URLS` list in [download_qgis_zips.py](download_qgis_zips.py).

## 📝 Notes

- The `qgis_downloads/` directory is ignored by git to avoid versioning large files
- The script automatically handles any download or parsing errors
- Files are processed in order from the most recent to the oldest version

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📄 License

See the [LICENSE](LICENSE) file for details.
