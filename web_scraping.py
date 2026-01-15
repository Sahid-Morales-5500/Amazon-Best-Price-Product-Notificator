from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from database import connection

# 1 - Pedir Producto
producto = input("ingresa el producto que deseas buscar en Amazon y presiona Enter: ")
url = f"https://www.amazon.es/s?k={producto.replace(' ', '+')}"

option = Options()
option.add_argument('--start-maximized')
option.add_argument('--disable-blink-features=AutomationControlled')
option.add_argument('--headless=new')
option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Driver:
driver = webdriver.Chrome(
    service = Service(ChromeDriverManager().install()),
    options= option
)

# Guardar Datos
Lista_Info = []
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

    # Mapeo de Datos de la pagina web para la Base de Datos
    for i,item in enumerate(resultados[:10]):
        titulo_tag = item.find('h2')
        precio_entero = item.find('span', class_ = 'a-price-whole')
        precio_decimal = item.find('span', class_ = 'a-price-fraction')
        img_tag = item.find('img', class_ = 's-image')
        url_img = img_tag['src'] if img_tag else None
        link_tag = item.find('a', class_='a-link-normal')

        if titulo_tag and precio_entero:
            titulo = img_tag['alt'] if img_tag else titulo_tag.text.strip()

            # Limpieza de Datos
            # Conversion de puntos a comas
            p_ent = precio_entero.text.replace('.','').replace(',','').strip()
            p_dec = precio_decimal.text.strip() if precio_decimal else '00'
            precio_final = f"{p_ent}.{p_dec}"

            # Conversion URL a Texto:
            url_img_txt = img_tag['src'] if img_tag else 'Sin Imagen'
            url_producto_txt = "https://www.amazon.es" + link_tag['href'] if link_tag else "Sin URL"

            # Print de los resultados de las paginas:
            print(f'[{i}] {titulo}... | {precio_final} €')

            # Informacion agregada a la lista.
            Lista_Info.append({
                'titulo': titulo, 
                'precio': precio_final, 
                'url': url_producto_txt,
                'imagen': url_img_txt

            })

        

except Exception as e:
    print(f"Error técnico: {e}")

finally:
    driver.quit()

from conexion import guardar_datos
guardar_datos(Lista_Info)

test_conn = connection()
if test_conn:
    print('Conexion Exitosa')
else: print('Conexion Fallida')


