# linkAuditor

Advanced Internal Link Auditor is a production-grade Python crawler that scans a website and detects all internal webpage links belonging to the same domain. It is designed for SEO audits, security analysis, research, and large CMS or Laravel-based websites.

The tool respects robots.txt, detects broken internal links, normalizes URLs to avoid duplication, and exports crawl results in both CSV and JSON formats.

---

## Features

- Crawls only internal links within the same domain
- Detects broken and error pages using HTTP status codes
- Respects robots.txt rules
- Normalizes URLs to prevent duplicates
- Filters only valid webpage URLs such as html and php
- Configurable crawl depth
- Multi-threaded crawling for performance
- Exports reports to CSV and JSON
- Suitable for SEO, security audits, and research use cases

---

## Requirements

- Python 3.8 or newer
- Internet access to the target website

### Python Dependencies

Install required libraries using pip:

```bash
pip install requests beautifulsoup4
