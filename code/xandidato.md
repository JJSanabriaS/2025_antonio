# ============================================
# APP INTERATIVO COMPLETO (SEM SERVIDOR)
# ============================================

# --- Instalação de dependências ---
%pip install -q selenium tabulate pandas ipywidgets openpyxl
from IPython.display import display, clear_output
import pandas as pd, time
import ipywidgets as widgets

# --- Configuração do Selenium (modo headless para Colab) ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# ============================================
# FUNÇÕES AUXILIARES (do seu scraper base)
# ============================================

def ajuste(url2, tiker, val_mom, strike, bid, ask):
    try:
        formula = (float(strike) - float(val_mom)) + (float(bid) - float(ask)) / (float(val_mom) + float(ask))
    except Exception:
        formula = 0.0
    return formula

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
            print(f"♻️ Tentando recarregar tabela... ({attempt + 1}/{retries})")
            time.sleep(1)
    return []

def prinp(url2):
    """Extrai e processa tabela de um ativo"""
    url = f"https://opcoes.net.br/opcoes/bovespa/{url2}"
    driver.get(url)
    try:
        table2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "divCotacaoAtual"))
        )
        val_mom = float(table2.text.split()[1].replace(".", "").replace(",", "."))
    except Exception:
        val_mom = 0.0

    try:
        table_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "tblListaOpc_wrapper"))
        )
    except TimeoutException:
        print("⚠️ Tabela não carregou.")
        return pd.DataFrame()

    table_data = extradados(table_container)
    resumo_list = []
    for i in range(0, len(table_data), 2):
        if i + 1 >= len(table_data):
            break
        strike, bid, ask = cadeiastring(i, table_data[i], table_data[i + 1])
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

def get_sel(driver, string):
    all_dataframes = pd.DataFrame()
    if string == "todo":
        retries = 3
        for attempt in range(retries):
            try:
                select_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "IdAcao"))
                )
                select = Select(select_element)
                all_options = select.options
                option_texts = [opt.text.strip() for opt in all_options if len(opt.text.strip()) > 1]
                print(f"📋 {len(option_texts)} opções encontradas.")
                break
            except (StaleElementReferenceException, TimeoutException):
                print(f"Tentando novamente... ({attempt+1}/{retries})")
                time.sleep(2)
        for opt in option_texts:
            print(f"➡️ {opt}")
            driver.get(f"https://opcoes.net.br/opcoes/bovespa/{opt}")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "tblListaOpc_wrapper"))
                )
                df_temp = prinp(opt)
                all_dataframes = pd.concat([all_dataframes, df_temp], ignore_index=True)
            except:
                continue
    else:
        df_temp = prinp(string)
        all_dataframes = pd.concat([all_dataframes, df_temp], ignore_index=True)
    return all_dataframes

# ============================================
# FUNÇÕES PARA POPULAR DROPDOWNS
# ============================================

def get_dropdown_options():
    """Obtém IdAcao e vencimentos"""
    driver.get("https://opcoes.net.br/opcoes/bovespa/AURE3")
    # Dropdown 1: IdAcao
    try:
        sel = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "IdAcao"))
        ))
        ativos = [o.text.strip() for o in sel.options if len(o.text.strip()) > 1]
        if "todo" not in ativos:
            ativos.insert(0, "todo")
    except Exception:
        ativos = ["todo"]

    # Dropdown 2: grade-vencimentos-dates
    try:
        venc_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "grade-vencimentos-dates"))
        )
        vencimentos = [v.text.strip() for v in venc_box.find_elements(By.ID, "listavencimentos") if v.text.strip()]
    except Exception:
        vencimentos = ["Nenhum"]

    return ativos, vencimentos

# ============================================
# INTERFACE IPYWIDGETS
# ============================================

ativos, vencimentos = get_dropdown_options()

ativo_dd = widgets.Dropdown(options=ativos, description='Ativo:')
venc_dd = widgets.Dropdown(options=vencimentos, description='Vencimento:')
threshold_input = widgets.FloatText(value=0.05, description='Threshold:')
run_btn = widgets.Button(description="Executar", button_style='success', icon='play')
download_btn = widgets.Button(description="Baixar CSV/XLSX", button_style='info', icon='download', disabled=True)
out = widgets.Output()
last_df = None

# ============================================
# CALLBACKS
# ============================================

def on_run_clicked(b):
    global last_df
    with out:
        clear_output(wait=True)
        ativo = ativo_dd.value
        threshold = threshold_input.value
        print(f"▶️ Executando scraper para {ativo} (threshold={threshold})...")
        df = get_sel(driver, ativo)
        if not df.empty:
            df["MinBidAsk"] = df[["Bid", "Ask"]].min(axis=1)
            df = df[df["MinBidAsk"] >= threshold]
            df = df.sort_values(by="Formula", ascending=False)
            display(df.head(30))
            last_df = df
            download_btn.disabled = False
        else:
            print("⚠️ Nenhum dado retornado.")
            download_btn.disabled = True

def on_download_clicked(b):
    if last_df is not None and not last_df.empty:
        last_df.to_csv("resultado.csv", index=False)
        last_df.to_excel("resultado.xlsx", index=False)
        from google.colab import files
        files.download("resultado.csv")
        files.download("resultado.xlsx")
        print("✅ Arquivos gerados.")
    else:
        print("⚠️ Nenhum resultado para baixar.")

run_btn.on_click(on_run_clicked)
download_btn.on_click(on_download_clicked)

# ============================================
# EXIBIÇÃO FINAL
# ============================================

ui = widgets.VBox([
    widgets.HTML("<h3>📊 Scraper B3 — Interface Única</h3>"),
    widgets.HBox([ativo_dd, venc_dd, threshold_input]),
    widgets.HBox([run_btn, download_btn]),
    out
])

display(ui)

