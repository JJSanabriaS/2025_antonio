# ============================================
# INTERFACE + SCRAPER UNIFICADOS PARA JUPYTER
# ============================================

%pip install -q selenium tabulate pandas ipywidgets openpyxl
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
from tabulate import tabulate
import ipywidgets as widgets

# ----------------------------------------------------------
# CONFIGURAÇÃO DO DRIVER (modo headless)
# ----------------------------------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

BASE_URL = "https://opcoes.net.br/opcoes/bovespa/AURE3"

# ----------------------------------------------------------
# FUNÇÕES DE SUPORTE
# ----------------------------------------------------------

def get_dropdown_options():
    """Obtém opções de 'IdAcao' e 'grade-vencimentos-dates'."""
    driver.get(BASE_URL)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "IdAcao")))

    # Obtém as ações disponíveis
    select_element = Select(driver.find_element(By.NAME, "IdAcao"))
    acao_opts = ["todo"] + [opt.text.strip() for opt in select_element.options if len(opt.text.strip()) > 1]

    # Obtém vencimentos (labels)
    #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "grade-vencimentos-dates")))
    #venc_div = driver.find_element(By.ID, "grade-vencimentos-dates")
    #labels = venc_div.find_elements(By.TAG_NAME, "label")
    vencimentos = driver.find_element(By.ID, "grade-vencimentos-dates")
    print("grade tipo")
    print(vencimentos.text)

    #vencimentos = [lbl.text.strip() for lbl in labels if len(lbl.text.strip()) > 0]

    return acao_opts, vencimentos


def ajuste(url2, tiker, val_mom, strike, bid, ask):
    try:
        return (float(strike) - float(val_mom)) + (float(bid) - float(ask)) / (float(val_mom) + float(ask))
    except Exception:
        return 0.0


def cadeiastring(datascall, datasput):
    try:
        strike = datascall[4] if len(datascall) > 26 else datascall[3]
        bid = datascall[11] or "0.0"
        ask = datasput[12] or "0.0"
        strike = strike.replace(".", "").replace(",", ".")
        bid = bid.replace(".", "").replace(",", ".")
        ask = ask.replace(".", "").replace(",", ".")
        return float(strike), float(bid), float(ask)
    except Exception:
        return 0.0, 0.0, 0.0


def extradados(table_container):
    """Extrai tabela com tolerância a StaleElementReferenceException."""
    retries = 3
    for attempt in range(retries):
        try:
            rows = table_container.find_elements(By.TAG_NAME, "tr")
            return [[cell.text for cell in row.find_elements(By.TAG_NAME, "td")] for row in rows]
        except StaleElementReferenceException:
            time.sleep(1)
    return []


def prinp(url2):
    """Extrai dados principais para um ativo específico."""
    url = f"https://opcoes.net.br/opcoes/bovespa/{url2}"
    driver.get(url)
    try:
        val_mom = float(driver.find_element(By.CSS_SELECTOR, "#divCotacaoAtual b").text.replace(".", "").replace(",", "."))
    except Exception:
        val_mom = 0.0

    try:
        table_container = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "tblListaOpc_wrapper")))
    except TimeoutException:
        return pd.DataFrame()

    table_data = extradados(table_container)
    if not table_data:
        return pd.DataFrame()

    resumo_list = []
    for i in range(0, len(table_data), 2):
        if i + 1 >= len(table_data):
            break
        strike, bid, ask = cadeiastring(table_data[i], table_data[i + 1])
        formula = ajuste(url2, table_data[i][0] if table_data[i] else "N/A", val_mom, strike, bid, ask)
        resumo_list.append({
            "Ativo": url2, "Ticker": table_data[i][0] if table_data[i] else "N/A",
            "ValMom": val_mom, "Strike": strike, "Bid": bid, "Ask": ask, "Formula": formula
        })
    return pd.DataFrame(resumo_list)

# ----------------------------------------------------------
# INTERFACE (IPYWIDGETS)
# ----------------------------------------------------------

acao_opts, vencimentos = get_dropdown_options()

acao_dd = widgets.Dropdown(
    options=acao_opts, description="Ativo:", style={"description_width": "70px"}, layout=widgets.Layout(width="300px")
)

venc_dd = widgets.Dropdown(
    options=vencimentos, description="Vencimento:", style={"description_width": "100px"}, layout=widgets.Layout(width="300px")
)

threshold_input = widgets.FloatText(
    value=0.05, description="Min Bid/Ask:", style={"description_width": "100px"}, layout=widgets.Layout(width="200px")
)

run_button = widgets.Button(
    description="Rodar Scraper", button_style="success", icon="play"
)

output = widgets.Output()

def on_run_button_clicked(b):
    with output:
        clear_output()
        ativo = acao_dd.value
        venc = venc_dd.value
        user_threshold = threshold_input.value

        print(f"🟢 Executando scraper com ativo='{ativo}', vencimento='{venc}', threshold={user_threshold}\n")

        df = prinp(ativo if ativo != "todo" else "AURE3")

        if df.empty:
            print("⚠️ Nenhum dado retornado.")
            return

        df["MinBidAsk"] = df[["Bid", "Ask"]].min(axis=1)
        df = df[df["MinBidAsk"] >= user_threshold]
        df_sorted = df.sort_values(by="Formula", ascending=False)

        print(f"✅ Total filtrado: {len(df_sorted)} registros.\n")
        display(df_sorted.head(30))

        # salvar
        df_sorted.to_csv("resultado.csv", index=False)
        df_sorted.to_excel("resultado.xlsx", index=False)
        print("💾 Arquivos gerados: resultado.csv e resultado.xlsx")

run_button.on_click(on_run_button_clicked)

ui = widgets.VBox([
    widgets.HBox([acao_dd, venc_dd]),
    widgets.HBox([threshold_input, run_button]),
    output
])

display(ui)

