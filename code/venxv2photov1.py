from selenium import webdriver

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Start browser
driver = webdriver.Chrome(options=chrome_options)# Or any other browser driver
driver.set_window_size(1920, 1080)  # Full HD size

driver.get("https://opcoes.net.br/opcoes/bovespa/AMBP3")

# Scroll the entire window horizontally to the right by 2000 pixels
driver.execute_script("window.scrollBy(200000, 0);")
try:
    # Wait for the checkbox to appear and click it
    checkbox = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "v2025-12-19"))
    )
    checkbox.click()
    print("✅ Checkbox #v2026-01-16 clicked successfully!")

except Exception as e:
    print("❌ Error clicking checkbox:", e)

# Optional: Screenshot confirmation
driver.save_screenshot("/content/checkbox_click.png")
print("📸 Screenshot saved as /content/checkbox_click.png")

# To scroll a specific element horizontally to the right:
# Assuming 'element' is a WebElement you've located
# element = driver.find_element(By.ID, "your_element_id")
# driver.execute_script("arguments[0].scrollLeft += 1000;", element) 
