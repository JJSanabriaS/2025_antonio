# =========================================
# STEP 1 — INSTALL DEPENDENCIES
# =========================================
!apt-get update -qq
!apt-get install -qq chromium-chromedriver
!pip install -q selenium ipywidgets pandas

# =========================================
# STEP 2 — IMPORTS
# =========================================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import ipywidgets as widgets
from IPython.display import display, clear_output
import time
import pandas as pd

# =========================================
# STEP 3 — DRIVER SETUP FUNCTION
# =========================================
def setup_driver():
    """Initialize Selenium Chrome driver (headless)."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    driver.set_window_size(1920, 1080)
    return driver, wait


# =========================================
# STEP 4 — SCRAPE FUNCTION
# =========================================
def get_vencimentos(driver, wait, url="https://opcoes.net.br/opcoes/bovespa/ABEV3"):
    """
    Accesses the provided URL and captures checkbox IDs and labels 
    from the '#grade-vencimentos-dates' section.
    Returns two lists: labels (for display) and values (real IDs).
    """
    print(f"🔗 Acessando página: {url}")
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "grade-vencimentos-dates")))
        time.sleep(2)
    except TimeoutException:
        print("⚠️ Timeout ao carregar a página.")
        return [], []

    container = driver.find_element(By.ID, "grade-vencimentos-dates")
    checkboxes = container.find_elements(By.TAG_NAME, "input")

    labels, values = [], []
    for cb in checkboxes:
        label_id = cb.get_attribute("id")
        data_du = cb.get_attribute("data-du")
        if label_id:
            label_text = f"{label_id} - {data_du} d.u."
            labels.append(label_text)
            values.append(label_id)

    print(f"✅ {len(labels)} vencimentos capturados.")
    print("labels   ",labels)
    print("values   ",values)
    return labels, values

# =========================================
# STEP 7 — MAIN EXECUTION
# =========================================
driver, wait = setup_driver()
labels, values = get_vencimentos(driver, wait)
driver.quit()

