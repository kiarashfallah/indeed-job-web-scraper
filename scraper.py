from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import os

# === Setup Chrome Profile ===
profile_path = r"scraping_profile"

options = Options()
options.add_argument(f"--user-data-dir={profile_path}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--lang=en-US")
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === Function to Scrape Jobs from a Single Page ===
def scrape_jobs_from_page(url):
    """Scrape job links from a single Indeed search page"""
    print(f"🔍 Scraping page: {url}")
    driver.get(url)
    time.sleep(20)

    # Scroll to load more jobs
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(3)

    # Collect job links
    job_cards = driver.find_elements(By.XPATH, '//a[contains(@class, "jcs-JobTitle")]')
    job_links = list({card.get_attribute('href') for card in job_cards if card.get_attribute('href')})
    
    print(f"✅ Found {len(job_links)} job links on this page")
    return job_links

# === Function to Scrape Individual Job Details ===
def scrape_job_details(link):
    """Scrape details from a single job page"""
    try:
        driver.get(link)
        time.sleep(5)

        # TITLE
        try:
            title = driver.find_element(By.XPATH, '//*[contains(@class,"e1tiznh50")]//span').text.strip()
        except:
            title = "N/A"

        # RATING
        try:
            rating = driver.find_element(By.XPATH, '//*[contains(@class,"css-79ia3k")]').text.strip()
        except:
            rating = "N/A"

        # LOCATION
        try:
            location = driver.find_element(By.XPATH, '//*[contains(@class,"css-dgqgie")]').text.strip()
        except:
            location = "N/A"

        # SALARY & CONTRACT TYPE
        try:
            income_time = driver.find_elements(By.XPATH, '//*[@id="salaryInfoAndJobType"]//*[contains(@class, "eu4oa1w0")]')
            income = income_time[0].text if len(income_time) > 0 else "N/A"
            contract_type = income_time[1].text if len(income_time) > 1 else "N/A"
        except:
            income = "N/A"
            contract_type = "N/A"

        # BENEFITS
        try:
            benefits = driver.find_element(By.XPATH, '//*[@id="benefits"]').text.strip()
        except:
            benefits = "N/A"

        return {
            "Title": title,
            "Rating": rating,
            "Location": location,
            "Salary": income,
            "Contract Type": contract_type,
            "Benefits": benefits,
            "Link": link
        }

    except Exception as e:
        print(f"❌ Error scraping job {link}: {e}")
        return None

# === Main Scraping Process ===
all_job_links = []
job_data = []

# First, scrape the initial search page
initial_url = "https://uk.indeed.com/jobs?q=data+engineer&l=London+East%2C+Greater+London&radius=100"
initial_links = scrape_jobs_from_page(initial_url)
all_job_links.extend(initial_links)

# Then, read additional URLs from CSV and scrape them
csv_path = r"links.csv"
if os.path.exists(csv_path):
    print(f"📂 Reading additional URLs from {csv_path}")
    
    # Read the CSV file (assuming URLs are in the first column)
    try:
        links_df = pd.read_csv(csv_path, header=None)  # No header expected
        additional_urls = links_df[0].tolist()  # Get first column as list
        
        print(f"📋 Found {len(additional_urls)} additional pages to scrape")
        
        # Scrape each additional page
        for url in additional_urls:
            if pd.notna(url) and url.strip():  # Check if URL is not empty
                page_links = scrape_jobs_from_page(url.strip())
                all_job_links.extend(page_links)
                time.sleep(5)  # Be respectful to the server
    
    except Exception as e:
        print(f"❌ Error reading links CSV: {e}")
else:
    print(f"⚠️ Links CSV file not found at {csv_path}")

# Remove duplicates
all_job_links = list(set(all_job_links))
print(f"🎯 Total unique job links collected: {len(all_job_links)}")

# === Scrape Each Job Page ===
print("🚀 Starting to scrape individual job details...")
total_jobs = len(all_job_links)

for i, link in enumerate(all_job_links, 1):
    print(f"📄 Scraping job {i}/{total_jobs}: {link[:50]}...")
    
    job_details = scrape_job_details(link)
    if job_details:
        job_data.append(job_details)
    
    # Add a small delay between requests
    time.sleep(2)
    
    # Save progress every 10 jobs (optional)
    if i % 10 == 0:
        temp_df = pd.DataFrame(job_data)
        temp_df.to_csv("indeed_jobs_progress.csv", index=False, encoding='utf-8-sig')
        print(f"💾 Progress saved: {len(job_data)} jobs scraped so far")

# === Save Final Results ===
if job_data:
    df = pd.DataFrame(job_data)
    df.to_csv("indeed_jobs_complete.csv", index=False, encoding='utf-8-sig')
    print(f"✅ All job data saved to indeed_jobs_complete.csv")
    print(f"📊 Total jobs scraped: {len(job_data)}")
    
    # Clean up progress file
    if os.path.exists("indeed_jobs_progress.csv"):
        os.remove("indeed_jobs_progress.csv")
else:
    print("❌ No job data was collected")

driver.quit()
print("🏁 Scraping completed!")