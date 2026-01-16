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
        print(f"Error de conexion BD: {e}")
        return None

def guardar_datos(lista):
    if not lista:
        return 0

    conn = get_db_connection()
    if not conn:
        return 0

    guardados = 0
    cur = None
    
    try:
        cur = conn.cursor()

        # SQL Producto
        sql_producto = """
            INSERT INTO Productos_Vigilados (nombre, url_amazon, imagen_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (url_amazon) DO UPDATE SET nombre = EXCLUDED.nombre
            RETURNING id_producto;
        """
        
        # SQL Precio
        sql_precio = """
            INSERT INTO Info_Product (id_producto, precio)
            VALUES (%s, %s);
        """

        for prod in lista:
            try:
                # Limpieza de precio
                precio_str = str(prod['precio']).replace('€', '').strip()
                if ',' in precio_str and precio_str.count('.') == 0:
                     precio_str = precio_str.replace(',', '.')
                
                precio_final = float(precio_str)

                # Insercion
                cur.execute(sql_producto, (prod['titulo'], prod['url'], prod['imagen']))
                id_generado = cur.fetchone()[0]
                cur.execute(sql_precio, (id_generado, precio_final))
                
                guardados += 1
            
            except ValueError:
                print(f"Error formato precio: {prod['titulo'][:20]}")
            except Exception as e_item:
                print(f"Error guardando item: {e_item}")

        conn.commit()
        print(f"Items guardados: {guardados}")

    except Exception as e:
        print(f"Error Transaccion: {e}")
        if conn: conn.rollback()
    
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
    return guardados
