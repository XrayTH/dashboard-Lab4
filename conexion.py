import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def crear_conexion():
    try:
        conexion = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        print("Conexión exitosa a la base de datos")
        return conexion

    except pymysql.MySQLError as error:
        print(f"Error al conectar a la base de datos: {error}")
        return None

def cerrar_conexion(conexion):
    """
    Cierra la conexión con la base de datos si está activa.
    """
    if conexion:
        conexion.close()
        print("Conexión cerrada")
