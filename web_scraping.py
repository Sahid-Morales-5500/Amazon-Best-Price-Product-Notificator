import customtkinter as ctk
import threading
from bs4 import BeautifulSoup
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- IMPORTACIÓN BD ---
try:
    from conexion import guardar_datos
except ImportError:
    def guardar_datos(lista): return 0

# --- TELEGRAM (INGRESA TUS TOKENS AQUI) ---



# --- CONFIGURACIÓN VISUAL ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Amazon Scraper Clean")
        self.geometry("750x850")
        self.configure(fg_color="#F0F3F5") 

        # === 1. FUENTES MÁS GRANDES Y ROBUSTAS (BOLD) ===
        # Título gigante
        self.FONT_TITLE = ("Segoe UI", 32, "bold") 
        # Texto general
        self.FONT_BODY = ("Segoe UI", 13, "bold")  
        # Botones
        self.FONT_BUTTON = ("Segoe UI", 14, "bold") 

        # Colores
        self.VERDE_PRINCIPAL = "#2CC985"
        self.VERDE_HOVER = "#24A36B"
        self.ROJO_DESMARCAR = "#FF5555"
        self.GRIS_BOTON = "#555555"
        
        # Estado del botón de selección
        self.todos_seleccionados = False

        # === TARJETA PRINCIPAL ===
        self.main_card = ctk.CTkFrame(
            self, fg_color="white", corner_radius=50, border_width=0
        )
        self.main_card.pack(pady=30, padx=30, fill="both", expand=True)

        # Título
        self.label = ctk.CTkLabel(
            self.main_card, 
            text="Amazon Scraper", 
            font=self.FONT_TITLE, # Fuente grande
            text_color="#333333"
        )
        self.label.pack(pady=(40, 15))

        # Buscador
        self.entry_producto = ctk.CTkEntry(
            self.main_card, 
            placeholder_text="Ej: Auriculares Bluetooth...", 
            width=450, height=50, corner_radius=25,
            border_color=self.VERDE_PRINCIPAL, border_width=2,
            fg_color="#FAFAFA",
            font=self.FONT_BODY 
        )
        self.entry_producto.pack(pady=10)
        
        # === 2. ACTIVAR CON TECLA ENTER ===
        self.entry_producto.bind("<Return>", self.iniciar_busqueda)

        # Botón Buscar
        self.btn_buscar = ctk.CTkButton(
            self.main_card, 
            text="🔎 BUSCAR", 
            command=self.iniciar_busqueda, 
            fg_color=self.VERDE_PRINCIPAL, hover_color=self.VERDE_HOVER,
            corner_radius=25, width=200, height=45,
            font=self.FONT_BUTTON
        )
        self.btn_buscar.pack(pady=5)

        # --- ÁREA DE HERRAMIENTAS ---
        self.frame_tools = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.frame_tools.pack(pady=(20, 5))

        self.label_res = ctk.CTkLabel(self.frame_tools, text="Resultados:", text_color="gray", font=self.FONT_BODY)
        self.label_res.pack(side="left", padx=10)

        # === 3. BOTÓN ÚNICO (TOGGLE) ===
        self.btn_toggle = ctk.CTkButton(
            self.frame_tools,
            text="✅ Marcar Todos",
            command=self.alternar_seleccion,
            width=120, height=30,
            fg_color=self.GRIS_BOTON, 
            hover_color="#333333",
            corner_radius=15,
            font=self.FONT_BODY
        )
        self.btn_toggle.pack(side="right", padx=10)

        # Scroll Frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_card, width=550, height=300, 
            corner_radius=25, fg_color="#F7F9F9"
        )
        self.scroll_frame.pack(pady=5)

        self.checkboxes_activos = [] 

        # Botón Guardar
        self.btn_guardar = ctk.CTkButton(
            self.main_card, 
            text="💾 GUARDAR SELECCIÓN", 
            command=self.guardar_seleccionados, 
            fg_color="#333333", hover_color="black",
            state="disabled", corner_radius=25, height=45,
            font=self.FONT_BUTTON
        )
        self.btn_guardar.pack(pady=10)

        # Log
        self.textbox = ctk.CTkTextbox(
            self.main_card, width=550, height=80, corner_radius=20, 
            fg_color="#FFFFFF", border_width=1, border_color="#EEEEEE",
            text_color="gray", font=("Consolas", 11)
        )
        self.textbox.pack(pady=(10, 30))

    def log(self, mensaje):
        self.textbox.insert("end", ">> " + mensaje + "\n")
        self.textbox.see("end")

    # === LÓGICA INTELIGENTE DEL BOTÓN ===
    def alternar_seleccion(self):
        if not self.checkboxes_activos: return

        self.todos_seleccionados = not self.todos_seleccionados

        if self.todos_seleccionados:
            # Marcar todo
            for chk, _ in self.checkboxes_activos: chk.select()
            self.btn_toggle.configure(text="❌ Desmarcar Todo", fg_color=self.ROJO_DESMARCAR, hover_color="#CC0000")
        else:
            # Desmarcar todo
            for chk, _ in self.checkboxes_activos: chk.deselect()
            self.btn_toggle.configure(text="✅ Marcar Todos", fg_color=self.GRIS_BOTON, hover_color="#333333")

    # Se añade event=None para que funcione con el Enter
    def iniciar_busqueda(self, event=None):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes_activos = []
        self.todos_seleccionados = False 
        self.btn_toggle.configure(text="✅ Marcar Todos", fg_color=self.GRIS_BOTON)
        self.btn_guardar.configure(state="disabled")
        
        hilo = threading.Thread(target=self.logica_scraping)
        hilo.start()

    def logica_scraping(self):
        producto = self.entry_producto.get()
        if not producto:
            self.log("⚠️ Escribe algo.")
            return

        self.log(f"🌱 Buscando '{producto}'...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            url = f"https://www.amazon.es/s?k={producto.replace(' ', '+')}"
            driver.get(url)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            resultados = []
            for item in items[:10]:
                try:
                    h2 = item.find('h2')
                    price = item.find('span', class_='a-price-whole')
                    link = item.find('a', class_='a-link-normal', href=True)
                    img = item.find('img', class_='s-image')

                    if h2 and price:
                        resultados.append({
                            'titulo': h2.text.strip(),
                            'precio': price.text.replace('.', '').replace(',', '.').strip(),
                            'url': "https://amazon.es" + link['href'], 
                            'imagen': img['src'] if img else ''
                        })
                except: continue
            
            if resultados: self.crear_checkboxes(resultados)
            else: self.log("🍃 Nada encontrado.")

        except Exception as e: self.log(f"Error: {e}")
        finally: driver.quit()

    def crear_checkboxes(self, lista):
        for datos in lista:
            texto = f"{datos['precio']}€  |  {datos['titulo'][:50]}..."
            chk = ctk.CTkCheckBox(
                self.scroll_frame, 
                text=texto, 
                text_color="#333333",
                fg_color=self.VERDE_PRINCIPAL,
                hover_color=self.VERDE_HOVER,
                corner_radius=100,
                font=self.FONT_BODY 
            )
            chk.pack(anchor="w", pady=8, padx=15)
            self.checkboxes_activos.append((chk, datos))
        
        self.btn_guardar.configure(state="normal")
        self.log("✨ Búsqueda lista.")

    def guardar_seleccionados(self):
        lista = [d for chk, d in self.checkboxes_activos if chk.get() == 1]
        if not lista: return
        guardar_datos(lista) 
        self.enviar_telegram(lista)
        self.log("✅ Guardado.")

    def enviar_telegram(self, lista):
        msg = "<b>SELECCIÓN GUARDADA</b>\n\n"
        for p in lista:
            msg += f"✅ {p['titulo'][:30]}...\n💰 <b>{p['precio']}€</b>\n🔗 <a href='{p['url']}'>Ver</a>\n\n"
        try:
            requests.post(f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage", 
                          data={"chat_id": CHAT_ID_TELEGRAM, "text": msg, "parse_mode": "HTML"})
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
