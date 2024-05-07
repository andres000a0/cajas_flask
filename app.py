from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from graficosDashboard import generate_chart_data as generate_dashboard_data
from graficaRegistroCajas import generar_datos_grafico as generar_datos_grafico
# import requests
from flask_mysqldb import MySQL
from functools import wraps
import csv

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
    productividad_data, inactividad_data = generate_dashboard_data()
    return render_template('views/dashboardContent.html', productividad_data=productividad_data, inactividad_data=inactividad_data)


@app.route('/compensacion')
@login_required
def compensacion():
    return render_template('views/compensacion.html')


@app.route('/registrosCajas')
@login_required
def registrosCajas():
    
    productividad_data_caja = generar_datos_grafico()
    
    return render_template('views/registrosCajas.html', productividad_data_caja=productividad_data_caja)


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

    # Consulta para obtener el tope de registros de la sede actual
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT tope_registros FROM topes_sede WHERE id_co = %s', (id_co,))
    tope_registros = cursor.fetchone()[0]
    cursor.close()

    # Consulta para obtener los registros de reg_cajeros filtrados por la sede del usuario y las fechas
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT identificacion, MAX(nombres) as nombres, COUNT(*) as cantidad_registros, 
            ROUND((COUNT(*) / %s) * 100, 2) as porcentaje
            FROM registro_mes 
            WHERE id_co = %s AND f9930_ts BETWEEN %s AND %s
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

    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT tope_registros FROM topes_sede WHERE id_co = %s', (id_co,))
    tope_registros = cursor.fetchone()[0]
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT identificacion, MAX(nombres) as nombres, COUNT(*) as cantidad_registros, 
            ROUND((COUNT(*) / %s) * 100, 2) as porcentaje
            FROM registro_mes 
            WHERE id_co = %s AND f9930_ts BETWEEN %s AND %s
            GROUP BY identificacion, nombres
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

# @app.teardown_appcontext
# def teardown_db(exception):
#     mysql.connection.close()
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4400)
