from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import os
from datetime import datetime

def scrape_naukri_jobs(start_page=1, max_jobs=10):
    options = Options()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')  # For background run

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    today = datetime.today().strftime('%Y-%m-%d')
    output_file = f'naukri_jobs_{today}.csv'

    # Create file with headers if not exists
    if not os.path.exists(output_file):
        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Title', 'Company', 'Experience', 'Salary',
                'Location', 'Posted', 'Openings', 'Skills',
                'Job Description', 'Link'
            ])

    job_count = 0
    current_page = start_page

    while job_count < max_jobs:
        url = f"https://www.naukri.com/software-developer-jobs-{current_page}"
        driver.get(url)
        time.sleep(3)
        print(f"\n📄 Scraping Page {current_page} => {url}")

        job_cards = driver.find_elements(By.CSS_SELECTOR, 'li.job-bx')  # ← UPDATE ME
        if not job_cards:
            print("⚠️ No job cards found — check selector!")
            driver.get_screenshot_as_file(f"debug_page_{current_page}.png")
            break
        print(f"🔎 Found {len(job_cards)} jobs")

        for job in job_cards:
            if job_count >= max_jobs:
                break
            try:
                job_link = job.find_element(By.CSS_SELECTOR, 'a.title').get_attribute('href')

                # Open job in new tab
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(job_link)
                time.sleep(2)

                def safe_get(by, value):
                    try:
                        return driver.find_element(by, value).text.strip()
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

                with open(output_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        title, company, experience, salary,
                        location, posted, openings, skills,
                        job_desc, job_link
                    ])

                job_count += 1
                print(f"✅ ({job_count}) Scraped: {title} at {company}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"⚠️ Error scraping job: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

        current_page += 1

    driver.quit()
    print(f"\n🎯 Scraping completed. Total jobs scraped: {job_count}. Saved to '{output_file}'.")

# Example run
scrape_naukri_jobs(start_page=1, max_jobs=10)
