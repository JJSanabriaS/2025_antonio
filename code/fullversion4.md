# =========================================
# JUPYTER NOTEBOOK - SCRAPER OPÇÕES BOVESPA
# =========================================

# =========================================
# STEP 0 — INSTALL DEPENDENCIES
# =========================================
!apt-get update -qq
!apt-get install -qq chromium-chromedriver
!pip install -q selenium tabulate ipywidgets pillow pandas requests

# =========================================
# STEP 1 — IMPORTS
# =========================================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from IPython.display import display, clear_output
import pandas as pd
import time
from datetime import datetime
import ipywidgets as widgets
from google.colab import files

# =========================================
# STEP 2 — DRIVER CONFIG
# =========================================
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)
driver.set_window_size(1920,1080)

# =========================================
# STEP 3 — SCRAPER FUNCTIONS
# =========================================
def get_vencimentos(driver, wait, url="https://opcoes.net.br/opcoes/bovespa/ABEV3"):
    driver.get(url)
    try:
        wait.until(EC.presence_of_element_located((By.ID,"grade-vencimentos-dates")))
        time.sleep(2)
    except TimeoutException:
        return [], []
    container = driver.find_element(By.ID,"grade-vencimentos-dates")
    checkboxes = container.find_elements(By.TAG_NAME,"input")
    labels, values = [], []
    for cb in checkboxes:
        label_id = cb.get_attribute("id")
        data_du = cb.get_attribute("data-du")
        if label_id:
            labels.append(f"{label_id} - {data_du} d.u.")
            values.append(label_id)
    return labels, values

def ajuste(url2, tiker, val_mom, strike, bid, ask):
    try:
        formula = (float(strike) - float(val_mom)) + (float(bid) - float(ask)) / (float(val_mom) + float(ask))
    except:
        formula = 0.0
    return formula

def armazem(df,name):
    df.to_csv(name+".csv", index=False)
    df.to_excel(name+".xlsx", index=False)
    files.download(name+".csv")
    files.download(name+".xlsx")
    return df

def cadeiastring(i, datascall, datasput):
    try:
        strike = datascall[4] if len(datascall) > 26 else datascall[3]
        bid = datascall[11] or "0.0"
        ask = datasput[12] or "0.0"
        strike = strike.replace(".", "").replace(",", ".")
        bid = bid.replace(".", "").replace(",", ".")
        ask = ask.replace(".", "").replace(",", ".")
        return float(strike), float(bid), float(ask)
    except:
        return 0.0,0.0,0.0

def extradados(table_container):
    retries = 3
    for attempt in range(retries):
        try:
            rows = table_container.find_elements(By.TAG_NAME,"tr")
            table_data = [[cell.text for cell in row.find_elements(By.TAG_NAME,"td")] for row in rows]
            return table_data
        except StaleElementReferenceException:
            time.sleep(1)
    return []

def prinp(url2):
    driver.get(f"https://opcoes.net.br/opcoes/bovespa/{url2}")
    try:
        table2 = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"divCotacaoAtual")))
        cotiz = table2.text.split()
        val_mom = float(cotiz[1].replace(".", "").replace(",", "."))
    except:
        val_mom = 0.0
    try:
        table_container = WebDriverWait(driver,15).until(EC.presence_of_element_located((By.ID,"tblListaOpc_wrapper")))
    except TimeoutException:
        return pd.DataFrame()
    table_data = extradados(table_container)
    if not table_data:
        return pd.DataFrame()
    resumo_list = []
    for i in range(3, len(table_data), 2):
        if i+1 >= len(table_data): break
        strike, bid, ask = cadeiastring(i, table_data[i], table_data[i+1])
        formula = ajuste(url2, table_data[i][0] if table_data[i] else "N/A", val_mom, strike, bid, ask)
        resumo_list.append({
            "Ativo": url2,
            "Ticker": table_data[i][0] if table_data[i] else "N/A",
            "ValMom": val_mom,
            "Strike": strike,
            "Bid": bid,
            "Ask": ask,
            "Formula": formula
        })
    return pd.DataFrame(resumo_list)

# =========================================
# STEP 4 — UI SETUP
# =========================================
btn_populate = widgets.Button(description="📥 Popula Inputs", button_style='success')
btn_run = widgets.Button(description="▶️ Executar Scraper", button_style='info', layout=widgets.Layout(display='none'))
btn_download = widgets.Button(description="💾 Download Dados", button_style='warning', layout=widgets.Layout(display='none'))

vencimentos_select = widgets.SelectMultiple(options=[], description='Vencimentos', rows=10)
ativos_dropdown = widgets.Dropdown(options=[], description='Ativos')

out = widgets.Output()
scraped_data = pd.DataFrame()
top30_data = pd.DataFrame()
vencimentos_values = []
option_texts = []

# =========================================
# STEP 5 — CALLBACKS
# =========================================
def populate_inputs(b):
    with out:
        clear_output()
        labels, values = get_vencimentos(driver, wait)
        vencimentos_select.options = labels
        global vencimentos_values
        vencimentos_values = values
        select_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,"IdAcao")))
        select = Select(select_element)
        global option_texts
        option_texts = [opt.text.strip() for opt in select.options if len(opt.text.strip())>1]
        ativos_dropdown.options = ["todo"] + option_texts
        btn_run.layout.display = 'inline-block'
        btn_download.layout.display = 'inline-block'
        print("✅ Inputs populados.")

def run_scraper(b):
    global scraped_data, top30_data
    with out:
        clear_output()
        ativo_sel = ativos_dropdown.value
        venc_sel = [vencimentos_values[vencimentos_select.options.index(v)] for v in vencimentos_select.value]
        
        print(f"▶️ Executando scraper para {ativo_sel}")
        print(f"Vencimentos selecionados: {vencimentos_select.value}")
        
        driver.get(f"https://opcoes.net.br/opcoes/bovespa/{ativo_sel}")
        
        # Limpar todos os checkboxes via JavaScript
        try:
            driver.execute_script("""
                document.querySelectorAll('#listadevencimentos input[type=checkbox]').forEach(cb => cb.checked = false);
            """)
            time.sleep(0.5)
        except:
            print("⚠️ Não foi possível limpar checkboxes via JS.")

        # Selecionar apenas os vencimentos escolhidos
        for v_id in venc_sel:
            try:
                cb = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, v_id))
                )
                if not cb.is_selected():
                    cb.click()
                    time.sleep(0.2)
            except TimeoutException:
                print(f"⚠️ Checkbox {v_id} não encontrado ou não clicável.")
            except StaleElementReferenceException:
                print(f"⚠️ Checkbox {v_id} ficou stale, pulando.")

        time.sleep(1)  # garante atualização da página após selecionar

        # Coleta de dados
        scraped_data = prinp(ativo_sel)
        if not scraped_data.empty:
            scraped_data["MinBidAsk"] = scraped_data[["Bid","Ask"]].min(axis=1)
            top30_data = scraped_data.sort_values(by="Formula", ascending=False).head(30)
            display(top30_data)
        else:
            print("⚠️ Nenhum dado retornado.")

def download_data(b):
    with out:
        if not scraped_data.empty and not top30_data.empty:
            armazem(scraped_data,"resumo")
            armazem(top30_data,"top30")
            print("💾 Download concluído.")
        else:
            print("⚠️ Nenhum dado para download.")

btn_populate.on_click(populate_inputs)
btn_run.on_click(run_scraper)
btn_download.on_click(download_data)

# =========================================
# STEP 6 — DISPLAY UI
# =========================================
display(widgets.VBox([btn_populate, widgets.HBox([vencimentos_select, ativos_dropdown]), btn_run, btn_download, out]))

