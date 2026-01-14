import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def connection():

    # Try to connect into the DB:
    try:
        conn = psycopg2.connect(
            host = os.getenv('DB_HOST'),
            port =  os.getenv('DB_PORT'),
            user = os.getenv('DB_USER'),
            password =  os.getenv('DB_PASSWORD'),
            dbname =  os.getenv('DB_NAME')
        )
        return conn
    except Exception as e:
        print(f'Conexion Fallida de la Base de Datos: {e}')
        return None