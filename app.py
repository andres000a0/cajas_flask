from flask import Flask, render_template, request, redirect, url_for, session
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
            session[username] = account[1]
            return redirect(url_for('dashboard'))
        else:
            msg = 'Usuario o contraseña incorrectos'
            cur.close()
    return render_template('inicioSesion.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    username = session['username']
    sede = session['sede']
    return render_template('dashboard.html', username=username, sede=sede)

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

if __name__ == '__main__':
    app.run(debug=True)