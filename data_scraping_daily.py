from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
import time
from datetime import datetime

def scrape_naukri_jobs(start_page=1, max_jobs=1000):
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"  # Adjust if needed
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')  # Optional headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    today = datetime.today().strftime('%Y-%m-%d')
    output_file = f'naukri_jobs_detailed_{today}.csv'

    # Load existing job links to skip duplicates
    existing_links = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) > 0:
                    existing_links.add(row[-1])

    # Create CSV with headers if not exists
    if not os.path.exists(output_file):
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Title', 'Company', 'Experience', 'Salary',
                'Location', 'Posted', 'Openings', 'Skills',
                'Job Description', 'Job Link'
            ])

    job_count = 0
    current_page = start_page

    while job_count < max_jobs:
        url = f"https://www.naukri.com/software-developer-jobs-{current_page}"
        print(f"\n🌐 Visiting Page {current_page} -> {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.srp-jobtuple-wrapper'))
            )
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'div.srp-jobtuple-wrapper')
        except Exception as e:
            print(f"⚠️ No job cards found: {e}")
            break

        print(f"🔍 Found {len(job_cards)} job cards")

        for job in job_cards:
            if job_count >= max_jobs:
                break

            try:
                job_link = job.find_element(By.CSS_SELECTOR, 'a.title').get_attribute('href')

                if job_link in existing_links:
                    print(f"⏩ Skipping already scraped: {job_link}")
                    continue

                # Open job in new tab
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(job_link)
                time.sleep(2)  # Allow content to load

                def safe_get(by, val):
                    try:
                        return driver.find_element(by, val).text.strip()
                    except:
                        return "Not specified"

                title = safe_get(By.CSS_SELECTOR, 'h1')
                company = safe_get(By.CSS_SELECTOR, 'a.pad-rt-8')
                experience = safe_get(By.XPATH, "//span[text()='Experience']/following-sibling::span")
                salary = safe_get(By.XPATH, "//span[text()='Salary']/following-sibling::span")
                location = safe_get(By.XPATH, "//span[text()='Location']/following-sibling::span")
                posted = safe_get(By.CLASS_NAME, 'timingWrapper')
                openings = safe_get(By.XPATH, "//span[contains(text(),'Openings')]/following-sibling::span")
                skills = safe_get(By.CLASS_NAME, 'key-skill')
                job_desc = safe_get(By.CLASS_NAME, 'dang-inner-html')

                # Write to CSV
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        title, company, experience, salary,
                        location, posted, openings, skills,
                        job_desc, job_link
                    ])

                job_count += 1
                existing_links.add(job_link)
                print(f"✅ ({job_count}) Saved: {title} at {company}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"⚠️ Error on job detail: {e}")
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    pass
                continue

        current_page += 1

    driver.quit()
    print(f"\n🎉 Finished! Total jobs scraped: {job_count}")
    print(f"📄 Data saved to: {output_file}")

# Run the scraper
scrape_naukri_jobs(start_page=1, max_jobs=1000)
