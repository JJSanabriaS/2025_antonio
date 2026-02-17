from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ipywidgets as widgets
from IPython.display import display

# =========================================
# Setup Chrome (Colab/headless compatible)
# =========================================
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # remove if you want to see browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)

# =========================================
# Function: Get vencimentos from page
# =========================================
def get_vencimentos(driver, url="https://opcoes.net.br/opcoes/bovespa/AMBP3"):
    """Opens the page and returns all available vencimento labels + IDs."""
    driver.get(url)
    time.sleep(3)
    driver.execute_script("window.scrollBy(200000, 0);")
    try:
        # ✅ FIX: use correct ID listavencimentos
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "listavencimentos"))
        )
        time.sleep(1)
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "#listavencimentos input[type='checkbox']")
        vencimentos = []
        for cb in checkboxes:
            try:
                label = cb.find_element(By.XPATH, "..").text.strip()
            except:
                label = cb.get_attribute("id")
            vencimentos.append({"id": cb.get_attribute("id"), "label": label})
        print(f"✅ Detected {len(vencimentos)} vencimentos.")
        return vencimentos
    except Exception as e:
        print("❌ Error detecting checkboxes:", e)
        return []

# =========================================
# Function: Clear and set vencimentos
# =========================================
def set_vencimentos(driver, ativo, selected_ids):
    """Opens user-defined ativo page, clears old selections, sets new ones, waits, and screenshots."""
    url = f"https://opcoes.net.br/opcoes/bovespa/{ativo.upper()}"
    print(f"🌐 Opening {url}")
    driver.get(url)
    time.sleep(3)
    driver.execute_script("window.scrollBy(200000, 0);")

    # Wait until vencimentos load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "listavencimentos"))
        )
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "#listavencimentos input[type='checkbox']")
        cleared = 0
        for cb in checkboxes:
            if cb.is_selected():
                driver.execute_script("arguments[0].click();", cb)
                cleared += 1
        print(f"✅ Cleared {cleared} previous checkboxes.")

        # Set selected vencimentos
        for cb in checkboxes:
            cb_id = cb.get_attribute("id")
            if cb_id in selected_ids:
                driver.execute_script("arguments[0].click();", cb)
                print(f"✅ Selected {cb_id}")

        print("⏳ Waiting 3 seconds for page update...")
        time.sleep(3)

        screenshot_path = f"/content/vencimentos.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved as {screenshot_path}")

    except Exception as e:
        print("❌ Error setting vencimentos:", e)

# =========================================
# Step 1 — Get vencimentos from initial page
# =========================================
vencimentos = get_vencimentos(driver)

# =========================================
# Step 2 — Create interactive widgets
# =========================================
if vencimentos:
    venc_map = {f"{v['label']} ({v['id']})": v['id'] for v in vencimentos}

    ativo_input = widgets.Text(
        value="AMBP3",
        description="Ativo:",
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='200px')
    )

    multiselect = widgets.SelectMultiple(
        options=list(venc_map.keys()),
        description="Vencimentos:",
        style={'description_width': 'initial'},
        rows=min(len(venc_map), 10),
        layout=widgets.Layout(width='50%')
    )

    button = widgets.Button(description="Set Selections", button_style='success')
    output = widgets.Output()

    # Button callback
    def on_button_click(b):
        with output:
            output.clear_output()
            ativo = ativo_input.value.strip()
            selected_labels = list(multiselect.value)
            selected_ids = [venc_map[label] for label in selected_labels]
            if not ativo or not selected_ids:
                print("⚠️ Please enter an ativo and select at least one vencimento.")
                return
            set_vencimentos(driver, ativo, selected_ids)

    button.on_click(on_button_click)

    # Display all widgets
    display(widgets.VBox([ativo_input, multiselect, button, output]))

else:
    print("⚠️ No vencimentos found. Check the ID used in get_vencimentos().")

