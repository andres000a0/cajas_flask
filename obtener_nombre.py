from flask import Flask, session
from flask_mysqldb import MySQL
import json

app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = '192.168.33.251'
app.config['MYSQL_USER'] = 'miguelos'
app.config['MYSQL_PASSWORD'] = 'Mosorio2022$'
app.config['MYSQL_DB'] = 'comp_cajeros'

mysql = MySQL(app)

def obtener_sede_usuario_actual():
    # Aquí suponemos que tienes guardado el ID del usuario en la sesión de Flask
    id_co = session['id_co']
    # Conecta a la base de datos
    cur = mysql.connection.cursor()

    # Consulta la sede del usuario actual en la tabla 'users'
    cur.execute("SELECT sede FROM users WHERE id = %s", (id_co,))
    sede = cur.fetchone()[0]

    # Cierra la conexión y devuelve la sede
    cur.close()
    return sede

# Función para obtener el nombre de la sede
def obtener_nombre_sede(sede):
    # Conecta a la base de datos
    cur = mysql.connection.cursor()

    # Consulta el nombre de la sede en la tabla 'topes_sede'
    cur.execute("SELECT nombre_sedes FROM topes_sede WHERE sede = %s", (sede,))
    nombre_sede = cur.fetchone()[0]

    # Cierra la conexión y devuelve el nombre de la sede
    cur.close()
    return nombre_sede

    print(nombre_sede)