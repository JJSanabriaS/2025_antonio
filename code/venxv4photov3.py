from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# =========================================
# Setup Chrome (Colab/headless compatible)
# =========================================
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # remove this line if you want to see browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)

# =========================================
# Open page
# =========================================
url = "https://opcoes.net.br/opcoes/bovespa/AMBP3"
driver.get(url)

# Give the page time to load JavaScript
time.sleep(3)

# Scroll horizontally (to ensure visibility)
driver.execute_script("window.scrollBy(200000, 0);")

# =========================================
# Clear all previously checked boxes
# =========================================
try:
    # Wait for the checkboxes container to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "listavencimentos"))
    )
    # Find all checkboxes within container
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "#listavencimentos input[type='checkbox']")
    
    cleared = 0
    for cb in checkboxes:
        if cb.is_selected():
            driver.execute_script("arguments[0].click();", cb)
            cleared += 1
    
    print(f"✅ Cleared {cleared} checked boxes.")
    
except Exception as e:
    print("❌ Could not clear checkboxes:", e)

# =========================================
# Click specific checkbox
# =========================================
try:
    checkbox = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "v2025-12-19"))
    )
    driver.execute_script("arguments[0].click();", checkbox)
    print("✅ Checkbox #v2025-12-19 clicked successfully!")
except Exception as e:
    print("❌ Error clicking checkbox:", e)

# =========================================
# Wait for update + screenshot
# =========================================
print("⏳ Waiting 3 seconds before taking screenshot...")
time.sleep(3)
driver.save_screenshot("/content/checkbox_click.png")
print("📸 Screenshot saved as /content/checkbox_click.png")

# driver.quit()

