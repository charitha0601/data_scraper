# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# import pandas as pd
# import time

# # Setup browser
# options = Options()
# options.add_argument("--start-maximized")
# # options.add_argument("--headless")  # uncomment for headless mode
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# base_url = "https://www.naukri.com/software-developer-jobs?refresh=1&offset={}"
# jobs = []
# offset = 1040
# main_window = driver.current_window_handle

# while True:
#     print(f"Scraping page with offset {offset}...")
#     driver.get(base_url.format(offset))

#     # Wait for job cards to load
#     try:
#         WebDriverWait(driver, 15).until(
#             EC.presence_of_all_elements_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
#         )
#     except Exception as e:
#         print("❌ Job cards did not load in time:", str(e))
#         break  # exit pagination loop if page doesn't load

#     job_cards = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
#     if not job_cards:
#         print("No more jobs found, ending scrape.")
#         break  # no jobs found, end loop

#     for card in job_cards:
#         try:
#             title = card.find_element(By.CLASS_NAME, "title").text
#         except:
#             title = ""
#         try:
#             company = card.find_element(By.CLASS_NAME, "comp-name").text
#         except:
#             company = ""
#         try:
#             location = card.find_element(By.CLASS_NAME, "locWdth").text
#         except:
#             location = ""
#         try:
#             job_link = card.find_element(By.CLASS_NAME, "title").get_attribute("href")
#         except:
#             job_link = None

#         try:
#             skill_elements = card.find_elements(By.CSS_SELECTOR, "ul.tags-gt li.dot-gt.tag-li")
#             skills = [elem.text.strip() for elem in skill_elements if elem.text.strip()]
#         except:
#             skills = []

#         salary = "Not disclosed"

#         if job_link:
#             driver.execute_script("window.open(arguments[0]);", job_link)
#             driver.switch_to.window(driver.window_handles[-1])
            
#             # Wait 2 seconds for page to load
#             time.sleep(2)

#             try:
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "div.styles_jhc__salary__jdfEC > span"))
#                 )
#                 salary = driver.find_element(By.CSS_SELECTOR, "div.styles_jhc__salary__jdfEC > span").text
#             except Exception as e:
#                 print(f"Salary not found for job: {title} | Error: {e}")
#                 salary = "Not disclosed"

#             driver.close()
#             driver.switch_to.window(main_window)

#         jobs.append({
#             "Job Title": title,
#             "Company": company,
#             "Location": location,
#             "Skills": skills,
#             "Salary": salary
#         })

#     # Increment offset for next page
#     offset += 20

# driver.save_screenshot("naukri_page.png")
# driver.quit()

# # Save to CSV
# df = pd.DataFrame(jobs)
# df.to_csv("naukri_jobs_detailed_paginated.csv", index=False)

# print(f"✅ Scraped {len(df)} jobs with detailed salary info from multiple pages.")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def scrape_naukri_jobs(max_jobs=2000, output_file="naukri_jobs_100.csv"):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    main_window = driver.current_window_handle

    scraped_links = set()
    page = 261
    jobs_scraped = 0
    all_data = []

    try:
        while jobs_scraped < max_jobs:
            url = f"https://www.naukri.com/software-developer-jobs-{page}?searchType=personalizedSearch"
            print(f"\n🔎 Scraping page: {page}")
            driver.get(url)

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
                )
            except:
                print("❌ No jobs found or page load failed.")
                break

            job_cards = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")

            for card in job_cards:
                if jobs_scraped >= max_jobs:
                    break

                try:
                    job_link = card.find_element(By.CLASS_NAME, "title").get_attribute("href")
                    if job_link in scraped_links:
                        continue
                    scraped_links.add(job_link)
                except:
                    continue

                try:
                    title = card.find_element(By.CLASS_NAME, "title").text
                except:
                    title = ""
                try:
                    company = card.find_element(By.CLASS_NAME, "comp-name").text
                except:
                    company = ""
                try:
                    location = card.find_element(By.CLASS_NAME, "locWdth").text
                except:
                    location = ""
                try:
                    skills = [el.text for el in card.find_elements(By.CSS_SELECTOR, "ul.tags-gt li.tag-li")]
                except:
                    skills = []

                posted = ""
                openings = ""
                applicants = ""

                try:
                    driver.execute_script("window.open(arguments[0]);", job_link)
                    driver.switch_to.window(driver.window_handles[-1])
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    # Salary
                    try:
                        salary_elem = driver.find_element(By.CSS_SELECTOR, "div.styles_jhc__salary__jdfEC > span")
                        salary = salary_elem.text
                    except:
                        salary = "Not disclosed"

                    # Posted Date
                    try:
                        posted = driver.find_element(By.XPATH, "//span[contains(text(),'Posted')]/following-sibling::span").text
                    except:
                        posted = ""

                    # Openings
                    try:
                        openings = driver.find_element(By.XPATH, "//span[contains(text(),'Openings')]/following-sibling::span").text
                    except:
                        openings = ""

                    # Applicants
                    try:
                        applicants = driver.find_element(By.XPATH, "//span[contains(text(),'Applicants')]/following-sibling::span").text
                    except:
                        applicants = ""

                    driver.close()
                    driver.switch_to.window(main_window)
                except:
                    driver.switch_to.window(main_window)
                    salary = "Not disclosed"


                job_data = {
                    "Job Title": title,
                    "Company": company,
                    "Location": location,
                    "Skills": ", ".join(skills),
                    "Salary": salary,
                    "Posted": posted,
                    "Openings": openings,
                    "Applicants": applicants
                }

                all_data.append(job_data)
                jobs_scraped += 1
                print(f"✅ {jobs_scraped}: {title} at {company}")

            page += 1
            time.sleep(2)

    finally:
        driver.quit()
        print(f"\n🎉 Finished scraping {jobs_scraped} jobs. Saving to CSV...")

        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False)
        print(f"📁 Data saved to {output_file} with {len(df)} records.")

# Run the scraper for up to 100 jobs but only from the first 5 pages
if __name__ == "__main__":
    scrape_naukri_jobs(max_jobs=2000)
