# ============================================
# Interface Web + Scraper integrado (Jupyter)
# ============================================

%pip install -q selenium tabulate pandas ipywidgets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from IPython.display import display, clear_output
import ipywidgets as widgets
import pandas as pd
import time
from datetime import datetime
from tabulate import tabulate
from google.colab import files

# ----------------------------------------------------------
# CONFIGURAÇÃO DO DRIVER
# ----------------------------------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# ----------------------------------------------------------
# FUNÇÕES AUXILIARES
# ----------------------------------------------------------
def ajuste(url2, tiker, val_mom, strike, bid, ask):
    try:
        formula = (float(strike) - float(val_mom)) + (float(bid) - float(ask)) / (float(val_mom) + float(ask))
    except Exception:
        formula = 0.0
    return formula

def armazem(df, name):
    df.to_csv(name + ".csv", index=False)
    df.to_excel(name + ".xlsx", index=False)
    try:
        files.download(name + ".csv")
        files.download(name + ".xlsx")
    except:
        pass
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
    except Exception:
        return 0.0, 0.0, 0.0

def extradados(table_container):
    retries = 3
    for attempt in range(retries):
        try:
            rows = table_container.find_elements(By.TAG_NAME, "tr")
            return [[cell.text for cell in row.find_elements(By.TAG_NAME, "td")] for row in rows]
        except StaleElementReferenceException:
            time.sleep(1)
    return []

def prinp(url2):
    """Extrai dados de um ativo e retorna DataFrame."""
    url = f"https://opcoes.net.br/opcoes/bovespa/{url2}"
    driver.get(url)
    try:
        table2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "divCotacaoAtual")))
        cotiz = table2.text.split()
        val_mom = float(cotiz[1].replace(".", "").replace(",", "."))
    except Exception:
        val_mom = 0.0

    try:
        table_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "tblListaOpc_wrapper"))
        )
    except TimeoutException:
        return pd.DataFrame()

    table_data = extradados(table_container)
    if not table_data:
        return pd.DataFrame()

    resumo_list = []
    for i in range(3, len(table_data), 2):
        if i + 1 >= len(table_data): break
        strike, bid, ask = cadeiastring(i, table_data[i], table_data[i + 1])
        formula = ajuste(url2, table_data[i][0] if table_data[i] else "N/A", val_mom, strike, bid, ask)
        resumo_list.append({
            "Ativo": url2, "Ticker": table_data[i][0] if table_data[i] else "N/A",
            "ValMom": val_mom, "Strike": strike, "Bid": bid, "Ask": ask, "Formula": formula
        })

    return pd.DataFrame(resumo_list)

def get_option_texts():
    """Obtém lista de opções (tickers) disponíveis."""
    driver.get("https://opcoes.net.br/opcoes/bovespa/AURE3")
    retries = 3
    for attempt in range(retries):
        try:
            select_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "IdAcao")))
            select = Select(select_element)
            texts = ["todo"] + [opt.text.strip() for opt in select.options if len(opt.text.strip()) > 1]
            return texts
        except Exception:
            time.sleep(2)
    return ["todo"]

# ----------------------------------------------------------
# INTERFACE (widgets)
# ----------------------------------------------------------
option_list = get_option_texts()

dropdown = widgets.Dropdown(
    options=option_list,
    description="Ativo:",
    style={'description_width': '80px'},
    layout=widgets.Layout(width='300px')
)

threshold_input = widgets.FloatText(
    value=-0.05,
    description='Threshold:',
    style={'description_width': '100px'},
    layout=widgets.Layout(width='250px')
)

run_button = widgets.Button(description="Executar Scraper", button_style='success')

output = widgets.Output()

display(widgets.HBox([dropdown, threshold_input, run_button]))
display(output)

# ----------------------------------------------------------
# AÇÃO AO CLICAR BOTÃO
# ----------------------------------------------------------
def run_scraper(_):
    clear_output(wait=True)
    display(widgets.HBox([dropdown, threshold_input, run_button]))
    display(output)

    ativo = dropdown.value
    user_threshold = threshold_input.value
    all_df = pd.DataFrame()

    with output:
        print(f"\n🚀 Iniciando coleta para: {ativo}")
        if ativo == "todo":
            print("Coletando todos os ativos disponíveis...")
            for name in option_list[1:]:
                print(f" → {name}")
                df_temp = prinp(name)
                all_df = pd.concat([all_df, df_temp], ignore_index=True)
        else:
            all_df = prinp(ativo)

        if all_df.empty:
            print("⚠️ Nenhum dado encontrado.")
            return

        print("previous filtering")
        display(all_df)
        armazem(all_df, "all_df")
        all_df["MinBidAsk"] = all_df[["Bid", "Ask"]].min(axis=1)
        filtered = all_df[all_df["MinBidAsk"] >= user_threshold]

        print(f"\n✅ {len(filtered)} registros após filtro Min(Bid,Ask) >= {user_threshold}")
        top30 = filtered.sort_values(by="Formula", ascending=False).head(30)
        display(top30)
        armazem(top30, "top30")

run_button.on_click(run_scraper)

