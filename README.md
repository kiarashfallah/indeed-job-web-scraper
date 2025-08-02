# Indeed Job Scraper

A robust web scraping tool for extracting job postings from Indeed.com with advanced anti-detection features.

## 🚀 Features

- **Multi-page scraping** with pagination support
- **Anti-detection mechanisms** (custom user agents, browser profiles)
- **Data extraction**: Job titles, ratings, locations, salaries, benefits
- **Progress tracking** with incremental saves
- **Duplicate removal** and data cleaning
- **CSV export** with UTF-8 encoding

## 🛠️ Technologies Used

- **Python 3.8+**
- **Selenium WebDriver** for browser automation
- **Pandas** for data manipulation
- **Chrome WebDriver** with custom configurations

## 📊 Sample Output

| Title | Rating | Location | Salary | Contract Type | Benefits |
|-------|--------|----------|--------|---------------|----------|
| Data Engineer | 4.2 | London | £45,000-£65,000 | Full-time | Health, Pension |

## 🚀 Quick Start

1. Clone the repository
```bash
git clone https://github.com/yourusername/indeed-job-scraper.git
cd indeed-job-scraper
