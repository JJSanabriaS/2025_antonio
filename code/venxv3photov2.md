# =========================================
# STEP 1 — INSTALL DEPENDENCIES
# =========================================
!apt-get update -qq
!apt-get install -qq chromium-chromedriver
!pip install -q selenium ipywidgets pandas

# =========================================
# STEP 2 — IMPORTS AND SETUP
# =========================================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import ipywidgets as widgets
from IPython.display import display, clear_output, IFrame
import time
import pandas as pd

# =========================================
# STEP 3 — DRIVER SETUP FUNCTION
# =========================================
def setup_driver():
    """Initialize Selenium Chrome driver (visible for inspection)."""
    chrome_options = Options()
    # Comment headless for visual inspection
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    driver.set_window_size(1920, 1080)
    return driver, wait

# =========================================
# STEP 4 — SCRAPE FUNCTION (GET CHECKBOX OPTIONS)
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
    return labels, values

# =========================================
# STEP 5 — FUNCTION: CLEAR, CLICK, WAIT, AND TAKE PHOTO
# =========================================
def set_vencimentos(driver, selected_ids):
    """Clear all checkboxes, then set selected ones, wait 3s, and save screenshot."""
    boxes = driver.find_elements(By.CSS_SELECTOR, "#grade-vencimentos-dates input[type='checkbox']")
    
    # Clear previous selections
    for box in boxes:
        if box.is_selected():
            driver.execute_script("arguments[0].click();", box)
    time.sleep(1)

    # Click user-selected checkboxes
    for box in boxes:
        if box.get_attribute("id") in selected_ids:
            driver.execute_script("arguments[0].click();", box)
            print(f"✅ Checkbox #{box.get_attribute('id')} clicked successfully!")
    
    # Wait 3 seconds before taking a screenshot
    print("⏳ Waiting 3 seconds before taking screenshot...")
    time.sleep(3)
    
    # Take screenshot
    screenshot_path = "/content/checkbox_click.png"
    driver.save_screenshot(screenshot_path)
    print(f"📸 Screenshot saved as {screenshot_path}")
    print("✅ Updated selections. Webpage left open for inspection.")

# =========================================
# STEP 6 — INTERACTIVE UI
# =========================================
driver, wait = setup_driver()
labels, values = get_vencimentos(driver, wait)

if not labels:
    print("⚠️ No vencimentos found.")
else:
    select_venc = widgets.SelectMultiple(
        options=labels,
        description='Vencimentos:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='60%', height='200px')
    )

    button_apply = widgets.Button(description="Aplicar Seleção", button_style='success')
    output = widgets.Output()

    def on_apply_clicked(b):
        with output:
            clear_output()
            selected_labels = list(select_venc.value)
            selected_ids = [values[labels.index(lbl)] for lbl in selected_labels]
            if not selected_ids:
                print("Nenhum vencimento selecionado.")
            else:
                set_vencimentos(driver, selected_ids)

    button_apply.on_click(on_apply_clicked)
    display(select_venc, button_apply, output)

# driver.quit()  # Keep open for inspection

