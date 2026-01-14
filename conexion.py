from database import connection

def guardar_datos(Lista_Info):
    if Lista_Info:
        print("\n" + "="*30)
        seleccion = input("Escribe el numero del producto a guardar (ej: 0): ")

        if seleccion.isdigit():
            idx = int(seleccion)
            if 0 <= idx < len(Lista_Info):
                prod = Lista_Info[idx] # El diccionario elegido
                
                # Conexion a la DB
                conn = connection()
                if conn:
                    try:
                        cur = conn.cursor()
                        
                        # 1. Insertar en tabla MAESTRA (Productos_Vigilados)
                        sql_producto = """
                            INSERT INTO Productos_Vigilados (nombre, url_amazon, imagen_url)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (url_amazon) DO UPDATE SET nombre = EXCLUDED.nombre
                            RETURNING id_producto;
                        """
                        cur.execute(sql_producto, (prod['titulo'], prod['url'], prod['imagen']))
                        
                        # Obtenemos el ID que Postgres generó
                        id_generado = cur.fetchone()[0]

                        # 2. Insertar en tabla HISTORIAL (Info_Product)
                        sql_precio = """
                            INSERT INTO Info_Product (id_producto, precio)
                            VALUES (%s, %s);
                        """
                        cur.execute(sql_precio, (id_generado, float(prod['precio'])))
                        
                        conn.commit()
                        print(f"\n✅ GUARDADO EXITOSO: {prod['titulo'][:30]}...")
                        
                    except Exception as e:
                        print(f"❌ Error SQL: {e}")
                        conn.rollback()
                    finally:
                        cur.close()
                        conn.close()
            else:
                print("Número fuera de rango.")
        else:
            print("Entrada inválida.")
    else:
        print("No se encontraron productos para guardar.")
