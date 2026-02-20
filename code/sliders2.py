# =========================================
# STEP 1 — INSTALL DEPENDENCIES
# =========================================
!apt-get update -qq
!apt-get install -qq chromium-chromedriver
!pip install -q selenium

# =========================================
# STEP 2 — IMPORTS & DRIVER SETUP
# =========================================
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

# =========================================
# STEP 3 — ABRE A PÁGINA E EXTRAI O STRIKE RANGE
# =========================================
try:
    url = "https://opcoes.net.br/opcoes/bovespa/AMBP3"
    driver.get(url)

    wait = WebDriverWait(driver, 15)

    # Aguarda o slider principal
    slider = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='grade-strikes-range']"))
        #//*[@id="grade-strikes-range"]
    )
#/html/body/div[1]/div[1]/div[1]/div[2]/div[3]/div[2]/div/span[1]
#html body div#divmiddle.padding-adjust div#grade-opcoes.container-fluid div div#divFiltros.noselect div#grade-strikes.grade-bloco div#grade-strikes-range div#strike-range.ui-slider.ui-corner-all.ui-slider-horizontal.ui-widget.ui-widget-content span.ui-slider-handle.ui-corner-all.ui-state-default
#span.ui-slider-handle:nth-child(2)
#span.ui-slider-handle:nth-child(3)
    # Obtém o valor atual do slider
    slider_handle1 = driver.find_element(By.CSS_SELECTOR, "span.ui-slider-handle:nth-child(2)")
    slider_handle2 = driver.find_element(By.CSS_SELECTOR, "span.ui-slider-handle:nth-child(3)")
    print("handler",slider_handle1.get_attribute("value"))
    print(slider_handle2.get_attribute("label"))
    value = slider.get_attribute("value")
    print(f"Valor atual do slider: {value}")
    print(slider.get.attribute("label"))

    # Obtém o valor mínimo e máximo do range
    min_value = slider.get_attribute("min")
    max_value = slider.get_attribute("max")

    print("=== STRIKE RANGE AMBP3 ===")
    print(f"Strike mínimo : {min_value}")
    print(f"Strike máximo : {max_value}")
    print(f"Strike atual  : {value}")

except Exception as e:
    print("Erro ao obter strike range:", e)

finally:
    driver.quit()

