# Instale ipywidgets se ainda não tiver
# !pip install ipywidgets requests beautifulsoup4 lxml

import ipywidgets as widgets
from IPython.display import display, clear_output
import requests
from bs4 import BeautifulSoup

# --- Função de scraping exemplo ---
def scrape_with_params(url, stock, deadline, threshold):
    """
    url: URL para raspar
    stock: opção selecionada no dropdown
    deadline: opção selecionada no dropdown
    threshold: float input
    """
    headers = {'User-Agent': 'jupyter-scraper/1.0'}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"error": str(e)}
    
    soup = BeautifulSoup(r.text, 'lxml')
    
    # Exemplo simples: retorna todos os textos do body contendo stock ou deadline
    items = []
    for el in soup.find_all(text=True):
        text = el.strip()
        if not text:
            continue
        # filtro fictício: mostra linhas contendo stock ou deadline
        if stock.lower() in text.lower() or deadline.lower() in text.lower():
            items.append(text)
    
    # aplica threshold fictício: só retorna se len(text) >= threshold
    filtered = [t for t in items if len(t) >= threshold]
    
    return {"url": url, "stock": stock, "deadline": deadline, "threshold": threshold, "results": filtered}

# --- Widgets ---
url_input = widgets.Text(
    value='https://example.com',
    description='URL:',
    layout=widgets.Layout(width='70%')
)

stock_dropdown = widgets.Dropdown(
    options=['AAPL', 'GOOG', 'MSFT', 'TSLA'],
    value='AAPL',
    description='Stock:'
)

deadline_dropdown = widgets.Dropdown(
    options=['1 week', '2 weeks', '1 month', '3 months'],
    value='1 week',
    description='Deadline:'
)

threshold_input = widgets.FloatText(
    value=10.0,
    description='Threshold:',
    step=1.0
)

scrape_btn = widgets.Button(
    description='Scrapear',
    button_style='success'
)

output = widgets.Output()

# --- Função de callback ---
def on_scrape_clicked(b):
    with output:
        clear_output()
        url = url_input.value.strip()
        stock = stock_dropdown.value
        deadline = deadline_dropdown.value
        threshold = threshold_input.value
        
        if not url:
            print("Preencha a URL!")
            return
        
        result = scrape_with_params(url, stock, deadline, threshold)
        if 'error' in result:
            print("Erro:", result['error'])
        else:
            print("Resultados encontrados:")
            for r in result['results']:
                print("-", r)

scrape_btn.on_click(on_scrape_clicked)

# --- Display UI ---
display(url_input, stock_dropdown, deadline_dropdown, threshold_input, scrape_btn, output)

