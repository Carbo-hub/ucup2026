# UCUP Kharkiv 2026 (Universities Cup) 🏆

> [!IMPORTANT]
> **BETA VERSION**: This project is currently in active development. 
> The information regarding sponsors, partners, and the final schedule is **preliminary** and intended for internal testing/demonstration purposes only. 
> Official data will be updated closer to the event start date.

Official website for the **Universities Cup Kharkiv 2026** — an intellectual IT tournament combining algorithmic programming, artificial intelligence, and creativity. Organized by the CMDA (КМАД) Department of NTU "KhPI" in cooperation with partner universities.

## 🚀 Features
- **FastAPI Backend**: Lightweight and blazing fast server to handle routing and dynamic content rendering.
- **Jinja2 Templating**: Clean separation of logic and presentation.
- **i18n Support**: Full bilingual support (Ukrainian & English) driven by dynamic JSON locales.
- **Zero-Database Architecture**: Configuration, schedules, and partner lists managed via `static/locales/` JSON files.
- **Responsive UI**: Modern design with CSS Grid/Flexbox, dynamic modal windows, and Google Material Symbols.

## 📁 Project Structure
```text
ucup2026/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License file
├── static/
│   ├── style.css           # Global stylesheet
│   ├── locales/            # i18n JSON dictionaries (uk.json, en.json)
│   └── logos/              # Graphic assets and sponsor logos
└── templates/
    ├── base.html           # Main layout (Header, Footer, Modals)
    └── index.html          # Dynamic sections (Hero, About, Schedule)