from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from graficosDashboard import generate_chart_data
# import requests
from flask_mysqldb import MySQL
from functools import wraps


app = Flask(__name__)
# conexión a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'comp_cajeros'

# inicia la base de datos
mysql = MySQL(app)
app.secret_key = 'L4v4quit4*'

# Bloquear rutas si no esta logeado!
def login_requiered(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# inicio de sesion
@app.route('/', methods=['GET', 'POST'])
def login():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'sede' in request.form:
        username = request.form['username']
        password = request.form['password']
        sede = request.form['sede']
        cur = mysql.connection.cursor()
        print(cur)
        cur.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s AND sede = %s' , (username, password, sede))
        account = cur.fetchone()
        cur.close()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]  # Aquí se establece el nombre de usuario en la sesión
            session['sede'] = account[4]
            return redirect(url_for('dashboardContent'))
        else:
            msg = 'Usuario o contraseña incorrectos'
            cur.close()
    return render_template('inicioSesion.html', msg=msg)

    # @app.route('/dashboard')
    # def dashboard():
    #     username = session['username']
    #     sede = session['sede']
    #     return render_template('dashboard.html', username=username, sede=sede)

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
    msg=""
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
        cur.execute("INSERT INTO users (username, password, cargo, sede) VALUES (%s, %s, %s, %s)", (username, password, cargo, sede))
        mysql.connection.commit()
        cur.close()
        msg = "Usuario registrado con exito!"
    else:
        msg = "Usuario no registrado!"
    
    return render_template('registrar.html', msg=msg)

# @app.route('/dashboard', methods = ['GET', 'POST'])
# def dashboard():
    
#     return render_template('/views/sidebar.html')

@app.route('/dashboardContent')
@login_requiered
def dashboardContent():
    productividad_data, inactividad_data = generate_chart_data()
    return render_template('views/dashboardContent.html', productividad_data=productividad_data, inactividad_data=inactividad_data)

@app.route('/compensacion')
@login_requiered
def compensacion():
    return render_template('views/compensacion.html')

@app.route('/registrosCajas')
@login_requiered
def registrosCajas():
    return render_template('views/registrosCajas.html')

@app.route('/productividadCajas')
@login_requiered
def productividadCajas():
    return render_template('views/productividadCajas.html')

@app.route('/tablas')
@login_requiered
def tablaRegistros():
    return render_template('views/tablaRegistros.html')

# consulta registros por fecha
@app.route('/registros_sede', methods=['POST'])
@login_requiered
def registros_sede():
    # Obtener los datos del formulario
    id_co = session['sede']

    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    # Consulta para obtener los registros de reg_cajeros filtrados por la sede del usuario y las fechas
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT identificacion, nombres, COUNT(*) as cantidad_registros, 
            COUNT(*) / 42012 * 100 as porcentaje
            FROM reg_cajeros 
            WHERE id_co = %s AND fechadato BETWEEN %s AND %s
            GROUP BY identificacion 
            ORDER BY cantidad_registros DESC;

    ''', (id_co, fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    print(registros)
    cursor.close()

    # Aquí puedes devolver los registros en formato JSON o procesarlos para renderizarlos en la tabla HTML
    return jsonify(registros) #render_template('views/tablaRegistros.html', rows=registros)

if __name__ == '__main__':
    app.run(debug=True)