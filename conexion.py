import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# --- CARGAR VARIABLES ---
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print(f"❌ Error conectando a Postgres: {e}")
        return None

def guardar_datos(lista):
    """
    Recibe la lista completa, abre UNA conexión y guarda todo.
    """
    if not lista:
        print("⚠️ La lista está vacía.")
        return 0

    conn = get_db_connection()
    if not conn:
        return 0

    guardados = 0
    cur = None
    
    try:
        cur = conn.cursor()
        print(f"💾 Iniciando guardado de {len(lista)} productos...")

        # 1. SQL para el PRODUCTO (Aquí nos aseguramos de guardar la URL)
        sql_producto = """
            INSERT INTO Productos_Vigilados (nombre, url_amazon, imagen_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (url_amazon) DO UPDATE SET nombre = EXCLUDED.nombre
            RETURNING id_producto;
        """
        
        # 2. SQL para el HISTORIAL DE PRECIO
        sql_precio = """
            INSERT INTO Info_Product (id_producto, precio)
            VALUES (%s, %s);
        """

        for prod in lista:
            try:
                # --- PASO A: Limpieza y Conversión de Precio ---
                # Esto es vital: Convertimos "1.200,50" a "1200.50" (formato numérico)
                # Incluso si main.py ya lo hizo, esto es un seguro de vida.
                precio_str = str(prod['precio']).replace('€', '').strip()
                # Si viene con coma decimal, la cambiamos a punto para Python
                if ',' in precio_str and precio_str.count('.') == 0:
                     precio_str = precio_str.replace(',', '.')
                
                precio_final = float(precio_str)

                # --- PASO B: Inserción en Base de Datos ---
                
                # 1. Insertamos el producto (Título, URL, Imagen)
                # IMPORTANTE: prod['url'] debe venir del main.py
                cur.execute(sql_producto, (prod['titulo'], prod['url'], prod['imagen']))
                
                # Obtenemos el ID que Postgres le asignó
                id_generado = cur.fetchone()[0]

                # 2. Insertamos el precio vinculado a ese ID
                cur.execute(sql_precio, (id_generado, precio_final))
                
                guardados += 1
                # print(f"   ↳ OK: {prod['titulo'][:15]}... ({precio_final}€)")
            
            except ValueError:
                print(f"   ❌ Error de formato de precio en: {prod['titulo'][:10]}...")
            except Exception as e_item:
                print(f"   ❌ Error guardando ítem: {e_item}")

        conn.commit() # Confirmamos todos los cambios al final
        print(f"🏁 Transacción completada. Total guardados: {guardados}")

    except Exception as e:
        print(f"❌ Error General de BD: {e}")
        if conn: conn.rollback()
    
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
    return guardados
