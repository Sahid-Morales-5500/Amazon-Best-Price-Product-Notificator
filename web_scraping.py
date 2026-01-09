from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 1 - Pedir Producto
producto = input("ingresa el producto que deseas buscar en Amazon y presiona Enter: ")
url = f"https://www.amazon.es/s?k={producto.replace(' ', '+')}"

option = Options()
option.add_argument('--start-maximized')
option.add_argument('--disable-blink-features=AutomationControlled')

# Driver:
driver = webdriver.Chrome(
    service = Service(ChromeDriverManager().install())
)


try:
    # Abrir pagina:
    driver.get(url)
    time.sleep(4)

    # Renderizar HTML:
    html = driver.page_source

    # Mirar Precios:
    sopa = BeautifulSoup(html, 'html.parser')
    resultados = sopa.find_all('div', {'data-component-type': 's-search-result'})
    print(f'Encontrados: {len(resultados)}')

    for item in resultados:
        titulo_tag = item.find('h2')
        precio_tag = item.find('span', class_ = 'a-price-whole')

        if titulo_tag:
            titulo = titulo_tag.text.strip()
            precio = precio_tag.text.strip() if precio_tag else 'Sin Precio'

            print(f'{titulo[:60]}... | {precio} €')



except Exception as e:
    print(f"Error técnico: {e}")

finally:
    driver.quit()
