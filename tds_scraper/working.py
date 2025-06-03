import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Setup driver (Chrome) ---
options = webdriver.ChromeOptions()
# Uncomment headless for running without UI
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

base_url = "https://tds.s-anand.net/#/2025-01/"

driver.get(base_url)

wait = WebDriverWait(driver, 20)

# Wait initial content load - wait for the markdown content to appear
wait.until(lambda d: d.find_element(By.CLASS_NAME, 'markdown-section').text.strip() != '')

# Find sidebar links (anchor tags inside nav.sidebar-nav with href starting with #/)
sidebar_links = driver.find_elements(By.CSS_SELECTOR, 'li.file > a[href^="#/"]')
print(f"Found {len(sidebar_links)} sidebar links:")
for link in sidebar_links:
    print(link.get_attribute('title'))  # printing title instead of href


# Extract unique titles (avoid duplicates)
hrefs = []
for link in sidebar_links:
    href = link.get_attribute('href')
    if href not in hrefs:
        hrefs.append(href)




data = []

for href in hrefs:
    print(f"Loading {href} ...")
    driver.get(href)
    
    # Wait for content to load: Wait until markdown-section text changes and is not empty
    wait.until(lambda d: d.find_element(By.CLASS_NAME, 'markdown-section').text.strip() != '')
    
    # Optional: small sleep to ensure content fully loaded (sometimes dynamic content)
    time.sleep(1)
    
    content_div = driver.find_element(By.CLASS_NAME, 'markdown-section')
    
    page_data = {
        "url": href,
        "content": content_div.text.strip()
    }
    data.append(page_data)

# Save all data to JSON
with open("tds_all_content.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ All content saved to tds_all_content.json")

driver.quit()
