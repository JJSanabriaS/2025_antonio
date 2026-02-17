# =========================================
# STEP 1 — INSTALL DEPENDENCIES
# =========================================
!apt-get update -qq
!apt-get install -qq chromium-chromedriver
!pip install -q selenium tabulate pillow pandas ipywidgets requests openpyxl

# =========================================
# STEP 2 — IMPORTS
# =========================================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from PIL import Image
from google.colab import files
import pandas as pd
import time
from datetime import datetime
from IPython.display import display, clear_output
import ipywidgets as widgets

# =========================================
# STEP 3 — DRIVER SETUP
# =========================================
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

# =========================================
# STEP 4 — SCRAPER FUNCTIONS
# =========================================
def get_vencimentos(driver, wait, url="https://opcoes.net.br/opcoes/bovespa/ABEV3"):
    """Captures checkbox labels and values from #grade-vencimentos-dates."""
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
            labels.append(f"{label_id} - {data_du} d.u.")
            values.append(label_id)
    print(f"✅ {len(labels)} vencimentos capturados.")
    return labels, values

def ajuste(url2, tiker, val_mom, strike, bid, ask):
    try:
        return (float(strike) - float(val_mom)) + (float(bid) - float(ask)) / (float(val_mom) + float(ask))
    except Exception:
        return 0.0

def armazem(df, name):
    df.to_csv(name + ".csv", index=False)
    df.to_excel(name + ".xlsx", index=False)
    files.download(name + ".csv")
    files.download(name + ".xlsx")

def prinp(url2):
    """Extrai dados de um ativo específico e retorna um resumo."""
    print(f"\n==== Iniciando {url2} ====")
    url = f"https://opcoes.net.br/opcoes/bovespa/{url2}"
    driver.get(url)
    try:
        table2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "divCotacaoAtual"))
        )
        cotiz = table2.text.split()
        val_mom = float(cotiz[1].replace(".", "").replace(",", "."))
    except Exception:
        val_mom = 0.0

    try:
        table_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "tblListaOpc_wrapper"))
        )
    except TimeoutException:
        print("⚠️ Tabela não carregou.")
        return pd.DataFrame()

    rows = table_container.find_elements(By.TAG_NAME, "tr")
    table_data = [[cell.text for cell in row.find_elements(By.TAG_NAME, "td")] for row in rows]
    resumo_list = []
    for i in range(3, len(table_data), 2):
        if i + 1 >= len(table_data): break
        try:
            strike = float(table_data[i][4].replace(".", "").replace(",", "."))
            bid = float(table_data[i][11].replace(".", "").replace(",", "."))
            ask = float(table_data[i+1][12].replace(".", "").replace(",", "."))
        except Exception:
            strike, bid, ask = 0.0, 0.0, 0.0
        formula = ajuste(url2, table_data[i][0], val_mom, strike, bid, ask)
        resumo_list.append({
            "Ativo": url2,
            "Ticker": table_data[i][0],
            "ValMom": val_mom,
            "Strike": strike,
            "Bid": bid,
            "Ask": ask,
            "Formula": formula
        })
    return pd.DataFrame(resumo_list)

# =========================================
# STEP 5 — UI SETUP
# =========================================
ativos_dropdown = widgets.Dropdown(description="Ativo:", options=["todo"], layout=widgets.Layout(width='50%'))
vencimentos_multi = widgets.SelectMultiple(description="Vencimentos:", options=[], layout=widgets.Layout(width='70%', height='150px'))
user_threshold = widgets.FloatText(value=-0.05, description="Threshold:", layout=widgets.Layout(width='30%'))

btn_populate = widgets.Button(description="1️⃣ Carregar opções", button_style="info")
btn_scrape = widgets.Button(description="2️⃣ Rodar scraper", button_style="warning", layout=widgets.Layout(display='none'))
btn_save = widgets.Button(description="3️⃣ Salvar resultados", button_style="success", layout=widgets.Layout(display='none'))

display(ativos_dropdown, vencimentos_multi, user_threshold, btn_populate, btn_scrape, btn_save)

# =========================================
# STEP 6 — LOGIC FUNCTIONS
# =========================================
def populate_fields(_):
    clear_output(wait=True)
    display(ativos_dropdown, vencimentos_multi, user_threshold, btn_populate, btn_scrape, btn_save)
    print("🔄 Coletando vencimentos e ativos...")
    labels, values = get_vencimentos(driver, wait)
    vencimentos_multi.options = list(zip(labels, values))
    driver.get("https://opcoes.net.br/opcoes/bovespa/ABEV3")
    select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "IdAcao"))))
    options = ["todo"] + [opt.text.strip() for opt in select.options if len(opt.text.strip()) > 1]
    ativos_dropdown.options = options
    print(f"✅ População concluída com {len(options)} ativos e {len(labels)} vencimentos.")
    btn_scrape.layout.display = ''
    btn_save.layout.display = 'none'

def run_scraper(_):
    clear_output(wait=True)
    display(ativos_dropdown, vencimentos_multi, user_threshold, btn_populate, btn_scrape, btn_save)
    ativo = ativos_dropdown.value
    threshold = user_threshold.value
    selected_vencs = list(vencimentos_multi.value)
    print(f"▶️ Rodando scraper para {ativo} com threshold {threshold} xom {selected_vencs}")
    for venc in selected_vencs:
        try:
            print(" venvimentos  ",venc)
            checkbox = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, venc)))
            driver.execute_script("arguments[0].click();", checkbox)
        except Exception as e:
            print(f"⚠️ Falha ao clicar em {venc}: {e}")
    
    try:
            driver.save_screenshot("/content/checkbox_click.png")
           # print("📸 Screenshot saved as /content/checkbox_click.png")
        except Exception as e:
            print(f"⚠️ Screenshot error: {e}")

    
    
    df = prinp(ativo)
    if not df.empty:
        print(f"📊 {len(df)} registros obtidos.")
        display(df.head(10))
        df["MinBidAsk"] = df[["Bid", "Ask"]].min(axis=1)
        df_filtered = df[df["MinBidAsk"] >= threshold]
        top30 = df_filtered.sort_values(by="Formula", ascending=False).head(30)
        display(top30)
        global resumo_df, top30_df
        resumo_df, top30_df = df, top30
        btn_save.layout.display = ''
    else:
        print("❌ Nenhum dado obtido.")

def save_results(_):
    if 'resumo_df' in globals() and not resumo_df.empty:
        armazem(resumo_df, "resumo_full")
        armazem(top30_df, "resumo_top30")
        print("💾 Resultados salvos com sucesso!")
    else:
        print("⚠️ Nenhum dado para salvar.")

# =========================================
# STEP 7 — LINK BUTTONS
# =========================================
btn_populate.on_click(populate_fields)
btn_scrape.on_click(run_scraper)
btn_save.on_click(save_results)

