# registros_mes.py
from flask import Flask, session, request
from flask_mysqldb import MySQL
from datetime import datetime
import json

app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = '192.168.33.251'
app.config['MYSQL_USER'] = 'miguelos'
app.config['MYSQL_PASSWORD'] = 'Mosorio2022$'
app.config['MYSQL_DB'] = 'comp_cajeros'

mysql = MySQL(app)

def registros_mes():
    cur = mysql.connection.cursor()
    id_co =session["sede"]
    
    fecha_inicio_mes = datetime.now().replace(day=1).strftime('%Y%m%d')
    
    # Ejecuta la consulta SQL
    cur.execute("""
    SELECT nombres, COUNT(identificacion) AS cantidad_registros 
        FROM registro_mes 
        WHERE id_co = %s AND fecha_dcto = %s 
        GROUP BY nombres 
        ORDER BY cantidad_registros DESC 
        LIMIT 1
    """, (id_co, fecha_inicio_mes))

    cajero_registros = cur.fetchall()
    
    
    cur.execute('''SELECT id_caja, COUNT(id_caja) AS cantidad_registros 
        FROM cajeros 
        WHERE id_co = %s AND fecha_dcto >= '20240301' AND fecha_dcto <= '20240331' 
        GROUP BY id_caja
        ORDER BY cantidad_registros DESC 
        LIMIT 1;
        ''', (id_co,))

    cajas_cantidad = cur.fetchall()
    # caja con mayor cantidad de registros
    
    cur.close()
    
    return cajero_registros, cajas_cantidad

