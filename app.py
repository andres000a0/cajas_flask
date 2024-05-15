from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from graficosDashboard import generate_chart_data as generate_dashboard_data
from registros_mes import registros_mes
# from obtener_nombre import obtener_nombre_sede
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
from functools import wraps
import csv
import json



TIEMPO_DE_INACTIVIDAD = 120

app = Flask(__name__)
# conexión a la base de datos
app.config['MYSQL_HOST'] = '192.168.33.251'
app.config['MYSQL_USER'] = 'miguelos'
app.config['MYSQL_PASSWORD'] = 'Mosorio2022$'
app.config['MYSQL_DB'] = 'comp_cajeros'
# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'comp_cajeros'

# inicia la base de datos
mysql = MySQL(app)
app.secret_key = 'L4v4quit4*'

# Bloquear rutas si no esta logeado!


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# inicio de sesion


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'sede' in request.form:
        username = request.form['username']
        password = request.form['password']
        sede = request.form['sede']
        cur = mysql.connection.cursor()
        print(cur)
        cur.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s AND sede = %s', (username, password, sede))
        account = cur.fetchone()
        cur.close()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            # Aquí se establece el nombre de usuario en la sesión
            session['username'] = account[1]
            session['sede'] = account[4]
            return redirect(url_for('dashboardContent'))
        else:
            msg = 'Usuario o contraseña incorrectos'
            cur.close()
    return render_template('inicioSesion.html', msg=msg)

# Cierre de sesion

# Actualiza la marca de tiempo en cada solicitud
@app.before_request
def actualizar_ultima_actividad():
    session.permanent = True
    session.modified = True
    session['ultima_actividad'] = datetime.now()

# Verifica si ha pasado el tiempo de inactividad permitido
@app.before_request
def verificar_timeout():
    ultima_actividad = session.get('ultima_actividad')
    if ultima_actividad is not None:
        tiempo_transcurrido = datetime.now() - ultima_actividad
        if tiempo_transcurrido > timedelta(seconds=TIEMPO_DE_INACTIVIDAD):
            # Si ha pasado el tiempo de inactividad, cierra la sesión del usuario
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('username', None)

@app.route('/login/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Registrar usuario


@app.route('/registrar', methods=['GET', 'POST'])
def registro():
    msg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['passwordConfirm']
        cargo = request.form['cargo']
        sede = request.form['sede']

        # Validar que las contraseñas coincidan
        if password != password_confirm:
            return 'Las contraseñas no coinciden'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password, cargo, sede) VALUES (%s, %s, %s, %s)",
                    (username, password, cargo, sede))
        mysql.connection.commit()
        cur.close()
        msg = "Usuario registrado con exito!"
    else:
        msg = "Usuario no registrado!"

    return render_template('registrar.html', msg=msg)


@app.route('/dashboardContent')
@login_required
def dashboardContent():
       
    
    cajero_registros, cajas_cantidad = registros_mes()
    productividad_data, inactividad_data = generate_dashboard_data()
    return render_template('views/dashboardContent.html', cajas_cantidad=cajas_cantidad,
                           cajero_registros=cajero_registros, 
                           productividad_data=productividad_data, 
                           inactividad_data=inactividad_data,
                        #    nombres_sede=nombres_sede, sedes=sedes
                           )


@app.route('/compensacion')
@login_required
def compensacion():
    return render_template('views/compensacion.html')


@app.route('/registrosCajas')
@login_required
def registrosCajas():
    
    
    # productividad_data_caja = generar_datos_grafico()
    
    return render_template('views/registrosCajas.html')


@app.route('/generar_datos_grafico', methods=['GET'])
@login_required
def generar_datos_grafico():
    
    cur = mysql.connection.cursor()
    id_co = session['sede']
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    # Convertir fechas a formato YYYY-MM-DD
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%Y%m%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%Y%m%d")

    # Consulta la base de datos para obtener los datos de productividad por caja en el rango de fechas especificado
    cur.execute('''SELECT id_caja, COUNT(*) AS productividad FROM cajeros 
                        WHERE id_co = %s AND fecha_dcto >= %s AND fecha_dcto <= %s 
                        GROUP BY id_caja''', (id_co, fecha_inicio, fecha_fin))
    cajas_productividad = cur.fetchall()
    print(cajas_productividad)
    # Procesa los datos para la gráfica
    cajas_nombres = []
    productividad = []

    for caja in cajas_productividad:
        cajas_nombres.append(caja[0])
        productividad.append(caja[1])

    cur.close()

    # Crear datos en el formato adecuado para Chart.js para productividad por registros
    productividad_data = {
        'labels': cajas_nombres,
        'datasets': [
            {
                'label': 'Productividad por Registros',
                'data': productividad,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1,
                'type': 'bar'
            }
        ]
    }

    # Convertir los datos a JSON
    productividad_data_json = json.dumps(productividad_data)

    return productividad_data_json                    


@app.route('/productividadCajas')
@login_required
def productividadCajas():
    return render_template('views/productividadCajas.html')


@app.route('/tablas')
@login_required
def tablaRegistros():
    return render_template('views/tablaRegistros.html')

# consulta registros por fecha


@app.route('/registros_sede', methods=['POST'])
@login_required
def registros_sede():
    # Obtener los datos del formulario
    id_co = session['sede']
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%Y%m%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%Y%m%d")
    
    # Determinar si el mes tiene 30 o 31 días
    fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y%m%d")
    dias_mes = fecha_inicio_dt.day
    tabla_tope_registros = 'tope_mes_30' if dias_mes == 30 else 'tope_registros'
    
    # Consulta para obtener el tope de registros de la sede actual
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT {} FROM topes_sede WHERE id_co = {}' .format(tabla_tope_registros, id_co,))
    tope_registros = cursor.fetchone()[0]
    cursor.close()

    # Consulta para obtener los registros de reg_cajeros filtrados por la sede del usuario y las fechas
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT identificacion, MAX(nombres) as nombres, COUNT(identificacion) as cantidad_registros,
            ROUND((COUNT(identificacion) / %s) * 100, 2) as porcentaje
            FROM registro_mes 
            WHERE id_co = %s AND fecha_dcto >= %s AND fecha_dcto <= %s
            GROUP BY identificacion
            ORDER BY cantidad_registros DESC;
    ''', (tope_registros, id_co, fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    cursor.close()

    return jsonify(registros)


@app.route('/exportar_csv', methods=['POST'])
@login_required
def exportar_csv():
    id_co = session['sede']
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    # convertir la fecha
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%Y%m%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%Y%m%d")
    #consulta para buscar la tope de registros
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT tope_mes_30 FROM topes_sede WHERE id_co = %s', (id_co,))
    tope_registros = cursor.fetchone()[0]
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT identificacion, MAX(nombres) as nombres, COUNT(identificacion) as cantidad_registros,
            ROUND((COUNT(identificacion) / %s) * 100, 2) as porcentaje
            FROM registro_mes 
            WHERE id_co = %s AND fecha_dcto >= %s AND fecha_dcto <= %s
            GROUP BY identificacion
            ORDER BY cantidad_registros DESC;
        ''', (tope_registros, id_co, fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    cursor.close()

    # Especifica el nombre del archivo CSV y su ubicación
    filename = 'registros.csv'

    # Especifica los encabezados de las columnas
    columnas = ['Cedula', 'Nombre', 'Registros', 'Porcentaje']

    # Escribe los datos en el archivo CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columnas)
        writer.writerows(registros)

    # Devuelve el archivo CSV como una respuesta para que el navegador lo descargue
    return send_file(filename, as_attachment=True)

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4400)
