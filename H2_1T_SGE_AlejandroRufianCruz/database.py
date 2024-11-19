import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_SETTINGS = {
    "host": "localhost",
    "user": "root",  # Cambia por tu usuario de MySQL
    "password": "curso",  # Cambia por tu contraseña de MySQL
    "database": "encuestas"
}

def create_connection():
    """Establece una conexión a la base de datos MySQL."""
    try:
        connection = mysql.connector.connect(**DB_SETTINGS)
        if connection.is_connected():
            print("¡Conexión exitosa a la base de datos MySQL!")
        return connection
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
        return None

def execute_query(query, data=None, fetch=False):
    """Ejecuta una consulta SQL con datos opcionales."""
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, data)
        if fetch:
            result = cursor.fetchall()
            return result
        connection.commit()
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()