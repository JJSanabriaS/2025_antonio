#xodigo a partir de 22

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
#wait = WebDriverWait(driver, timeout=2)
#wait.until(lambda _ : revealed.is_displayed())



# Navigate to the webpage containing the div-based table
url="https://opcoes.net.br/opcoes/bovespa/AURE3"
driver.get(url) # Replace with the actual URL
response = requests.get(url)
text_content = response.text
# Wait for the table element to be present (adjust locator as needed)
# This assumes the main table div has a specific class, e.g., 'table-container'
url_list = url.split('/')
print("papel:  "+url_list[len(url_list)-1])
print("\n")
#<select name="IdAcao"><option></option>value

select_element = driver.find_element(By.NAME, "IdAcao")

# 2. Create a Select object
select = Select(select_element)

# 3. Get all available options (WebElements)
all_options = select.options

# 4. Iterate through the options and extract their text or value attributes
print("Visible text of all options:")
for option in all_options:
    print(option.text)
    print("https://opcoes.net.br/opcoes/bovespa/"+option.text)

#print("\nValue attribute of all options:")
#for option in all_options:
    #print(option.get_attribute("value"))

# 5. Get the currently selected option(s)
# For single-select dropdowns:
#selected_option = select.first_selected_option
#print(f"\nCurrently selected option (text): {selected_option.text}")
#print(f"Currently selected option (value): {selected_option.get_attribute('value')}")

# For multi-select dropdowns (if applicable):
# selected_options = select.all_selected_options
# print("\nAll currently selected options:")
# for option in selected_options:
#     print(option.text)

# Close the browser
driver.quit()
