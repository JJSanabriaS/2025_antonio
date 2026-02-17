import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# --------------------------
# Selenium setup (headless)
# --------------------------
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    return driver, wait

driver, wait = init_driver()

# --------------------------
# Functions
# --------------------------
def ajuste(url2, tiker, val_mom, strike, bid, ask):
    try:
        formula = (float(strike) - float(val_mom)) + (float(bid) - float(ask)) / (float(val_mom) + float(ask))
    except:
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
    except:
        return 0.0, 0.0, 0.0

def extradados(table_container):
    retries = 3
    for attempt in range(retries):
        try:
            rows = table_container.find_elements(By.TAG_NAME, "tr")
            table_data = [[cell.text for cell in row.find_elements(By.TAG_NAME, "td")] for row in rows]
            return table_data
        except StaleElementReferenceException:
            time.sleep(1)
    return []

def prinp(url2):
    driver.get(f"https://opcoes.net.br/opcoes/bovespa/{url2}")
    try:
        table2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "divCotacaoAtual"))
        )
        cotiz = table2.text.split()
        val_mom = float(cotiz[1].replace(".", "").replace(",", "."))
    except:
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
    if string == 'todo':
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "IdAcao"))
        )
        select = Select(select_element)
        option_texts = [opt.text.strip() for opt in select.options if len(opt.text.strip()) > 1]

        for option_text in option_texts:
            driver.get(f"https://opcoes.net.br/opcoes/bovespa/{option_text}")
            df_temp = prinp(option_text)
            if not df_temp.empty:
                all_dataframes = pd.concat([all_dataframes, df_temp], ignore_index=True)
    else:
        df_temp = prinp(string)
        all_dataframes = pd.concat([all_dataframes, df_temp], ignore_index=True)

    return all_dataframes

# --------------------------
# Streamlit UI
# --------------------------
st.title("💹 Bovespa Options Scraper")

ativo = st.text_input("Ativo (ex: ABEV3, todo)", "todo")
threshold = st.number_input("Threshold Min(Bid, Ask)", min_value=0.0, value=0.05, step=0.01)

if st.button("Executar Scraper"):
    with st.spinner("Coletando dados..."):
        df = get_sel(driver, ativo)
        if df.empty:
            st.warning("Nenhum dado encontrado.")
        else:
            df["MinBidAsk"] = df[["Bid","Ask"]].min(axis=1)
            df_filtered = df[df["MinBidAsk"] >= threshold]
            top30 = df_filtered.sort_values(by="Formula", ascending=False).head(30)
            st.success("✅ Scraper finalizado!")
            st.subheader("Top 30")
            st.dataframe(top30)
            df_filtered.to_csv("full.csv", index=False)
            top30.to_csv("top30.csv", index=False)
            st.download_button("Baixar full.csv", data=open("full.csv","rb"), file_name="full.csv")
            st.download_button("Baixar top30.csv", data=open("top30.csv","rb"), file_name="top30.csv")

