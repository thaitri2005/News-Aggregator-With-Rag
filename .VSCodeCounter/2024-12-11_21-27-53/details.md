# Details

Date : 2024-12-11 21:27:53

Directory d:\\RAG\\News-Aggregator-With-Rag

Total : 46 files,  22416 codes, 218 comments, 428 blanks, all 23062 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [README.md](/README.md) | Markdown | 143 | 0 | 52 | 195 |
| [app/.dockerignore](/app/.dockerignore) | Ignore | 19 | 10 | 9 | 38 |
| [app/Dockerfile](/app/Dockerfile) | Docker | 17 | 10 | 10 | 37 |
| [app/__init__.py](/app/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/api/__init__.py](/app/api/__init__.py) | Python | 0 | 1 | 0 | 1 |
| [app/api/gemini_integration.py](/app/api/gemini_integration.py) | Python | 73 | 6 | 14 | 93 |
| [app/api/routes.py](/app/api/routes.py) | Python | 158 | 14 | 36 | 208 |
| [app/api/scheduler.py](/app/api/scheduler.py) | Python | 22 | 1 | 6 | 29 |
| [app/api/scrapers/__init__.py](/app/api/scrapers/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/api/scrapers/dantri_rss_scraper.py](/app/api/scrapers/dantri_rss_scraper.py) | Python | 127 | 8 | 27 | 162 |
| [app/api/scrapers/thanhnien_rss_scraper.py](/app/api/scrapers/thanhnien_rss_scraper.py) | Python | 108 | 4 | 18 | 130 |
| [app/api/scrapers/tuoitre_scraper.py](/app/api/scrapers/tuoitre_scraper.py) | Python | 102 | 7 | 18 | 127 |
| [app/api/scrapers/vietnamnet_rss_scraper.py](/app/api/scrapers/vietnamnet_rss_scraper.py) | Python | 74 | 4 | 15 | 93 |
| [app/api/scrapers/vnexpress_scraper.py](/app/api/scrapers/vnexpress_scraper.py) | Python | 51 | 5 | 13 | 69 |
| [app/main.py](/app/main.py) | Python | 13 | 3 | 6 | 22 |
| [app/models/__init__.py](/app/models/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/models/article_model.py](/app/models/article_model.py) | Python | 42 | 1 | 5 | 48 |
| [app/requirements.txt](/app/requirements.txt) | pip requirements | 17 | 1 | 0 | 18 |
| [app/services/__init__.py](/app/services/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/services/article_processor.py](/app/services/article_processor.py) | Python | 71 | 4 | 9 | 84 |
| [app/services/vector_db_service.py](/app/services/vector_db_service.py) | Python | 128 | 5 | 21 | 154 |
| [app/services/vectorizer_service.py](/app/services/vectorizer_service.py) | Python | 33 | 4 | 6 | 43 |
| [app/utils/__init__.py](/app/utils/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/utils/common.py](/app/utils/common.py) | Python | 10 | 1 | 2 | 13 |
| [app/utils/logging_config.py](/app/utils/logging_config.py) | Python | 36 | 1 | 2 | 39 |
| [app/utils/scraper_helpers.py](/app/utils/scraper_helpers.py) | Python | 87 | 7 | 18 | 112 |
| [deployment/docker-compose.yml](/deployment/docker-compose.yml) | YAML | 46 | 1 | 4 | 51 |
| [frontend/.dockerignore](/frontend/.dockerignore) | Ignore | 16 | 9 | 8 | 33 |
| [frontend/Dockerfile](/frontend/Dockerfile) | Docker | 7 | 6 | 5 | 18 |
| [frontend/package-lock.json](/frontend/package-lock.json) | JSON | 20,198 | 0 | 1 | 20,199 |
| [frontend/package.json](/frontend/package.json) | JSON | 52 | 0 | 1 | 53 |
| [frontend/public/index.html](/frontend/public/index.html) | HTML | 20 | 23 | 1 | 44 |
| [frontend/public/manifest.json](/frontend/public/manifest.json) | JSON | 25 | 0 | 1 | 26 |
| [frontend/src/App.js](/frontend/src/App.js) | JavaScript | 184 | 5 | 25 | 214 |
| [frontend/src/App.test.js](/frontend/src/App.test.js) | JavaScript | 7 | 0 | 2 | 9 |
| [frontend/src/components/Article.js](/frontend/src/components/Article.js) | JavaScript | 39 | 1 | 6 | 46 |
| [frontend/src/components/SummaryPanel.js](/frontend/src/components/SummaryPanel.js) | JavaScript | 10 | 1 | 3 | 14 |
| [frontend/src/contexts/AppContext.js](/frontend/src/contexts/AppContext.js) | JavaScript | 110 | 15 | 18 | 143 |
| [frontend/src/contexts/ThemeContext.js](/frontend/src/contexts/ThemeContext.js) | JavaScript | 14 | 4 | 6 | 24 |
| [frontend/src/index.css](/frontend/src/index.css) | CSS | 120 | 6 | 20 | 146 |
| [frontend/src/index.js](/frontend/src/index.js) | JavaScript | 18 | 3 | 4 | 25 |
| [frontend/src/logo.svg](/frontend/src/logo.svg) | XML | 1 | 0 | 0 | 1 |
| [frontend/src/reportWebVitals.js](/frontend/src/reportWebVitals.js) | JavaScript | 12 | 0 | 2 | 14 |
| [frontend/src/services/api.js](/frontend/src/services/api.js) | JavaScript | 76 | 38 | 8 | 122 |
| [frontend/src/setupTests.js](/frontend/src/setupTests.js) | JavaScript | 1 | 4 | 1 | 6 |
| [frontend/src/styles/App.css](/frontend/src/styles/App.css) | CSS | 129 | 5 | 20 | 154 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)