#xodigo a partir de 22
#https://www.youtube.com/watch?v=BcOqtHS_I3c

%pip install -q selenium
%pip install -q tabulate
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image
from IPython.display import display
from google.colab import files
import requests
from selenium.webdriver.support.ui import Select
from tabulate import tabulate
import pandas as pd
#from google.colab import drive drive.mount('/content/drive') ##you will need to authenticate using an authorization code. Content/ drive is the default folder.
from google.colab import files
from google.colab import drive

# Configure Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Initialize the WebDriver (e.g., Chrome) with the configured options
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, timeout=10) # Increased timeout for waiting

def prinp():
    strike=0
    bid=0
    ask=0
    # Navigate to the webpage containing the div-based table
    url="https://opcoes.net.br/opcoes/bovespa/AMBP3"
    #url="https://opcoes.net.br/opcoes/bovespa/ABEV3"
    quantcolumns=36
    driver.get(url) # Replace with the actual URL
    response = requests.get(url)
    text_content = response.text
    # Wait for the table element to be present (adjust locator as needed)
    # This assumes the main table div has a specific class, e.g., 'table-container'
    url_list = url.split('/')
    print("papel:  "+url_list[len(url_list)-1])
    print("\n")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    vencimentos = driver.find_element(By.ID, "grade-vencimentos-dates")
    # Use WebDriverWait to wait for the checkbox to be clickable
    # Changed the locator to be more specific if possible, targeting the checkbox within the vencimentos element
    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='grade-vencimentos-dates']//input[@type='checkbox']")))
    print("grade tipo")
    print(vencimentos.text)
    ids = driver.find_elements(By.TAG_NAME,"input")
    vencimentos=[]
    datas=[]
    for ii in ids:
        #print ii.tag_name
        #print (ii.get_attribute('id'))    # id name as string
        datas.append(ii.get_attribute('id'))
        print("label    ",ii.get_attribute('label'))
        print("value   ",ii.get_attribute('value'))
        print("data-du   ",ii.get_attribute('data-du'))
        vencimentos.append(ii.get_attribute('selected'))

    # Assuming ids[3] is the correct checkbox based on previous attempts
    # if not ids[3].is_selected():
    #     ids[3].click()


    print(checkbox)
    print("len  ", len(datas))
    box=len(datas)-5
    print(datas[0:3])
    print(vencimentos[0:3])
    print("labels  ", datas[3:box])
    print("selexted  ",vencimentos[3:box])


    # Use JavaScript to click the checkbox
    driver.execute_script("arguments[0].click();", checkbox)
    print("Checkbox selected using JavaScript.")

prinp()

# Close the browser
driver.quit()
