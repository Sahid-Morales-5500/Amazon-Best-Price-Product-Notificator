import requests
from bs4 import BeautifulSoup
import time

url = "https://www.amazon.es/s?k=xiaomi+poco"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1"
}

try:
    time.sleep(2)
    respuesta = requests.get(url, headers=headers)

    if respuesta.status_code == 503:
        print("Error 503: Bloqueo de Amazon. Cambia tu IP.")
        
    elif respuesta.status_code == 200:
        if "captcha" in respuesta.text.lower():
            print("Error: Amazon pide resolver Captcha.")
        else:
            sopa = BeautifulSoup(respuesta.text, 'html.parser')
            resultados = sopa.find_all('div', {"data-component-type": "s-search-result"})

            print(f"Encontrados: {len(resultados)}")

            for producto in resultados:
                titulo_tag = producto.find('h2')
                precio_tag = producto.find('span', class_='a-price-whole')

                if titulo_tag:
                    titulo = titulo_tag.text.strip()
                    precio = precio_tag.text.strip() if precio_tag else "Sin precio"
                    
                    print(f"{titulo[:60]}... | {precio} euros")

    else:
        print(f"Error desconocido: {respuesta.status_code}")

except Exception as e:
    print(f"Error técnico: {e}")
