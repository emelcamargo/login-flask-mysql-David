import os
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from models import db, Usuario
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_super_segura')

# Configuración de la conexión a MySQL (dinámica para local y Railway)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'login_flask_db')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con la app
db.init_app(app)

# Crear las tablas automáticamente si no existen
with app.app_context():
  db.create_all()


@app.route('/')
def home():
  if 'usuario' in session:
    return redirect(url_for('inicio'))
  return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    nombre_usuario = request.form.get('usuario')
    password = request.form.get('password')

    # Buscar usuario en la base de datos MySQL
    user = Usuario.query.filter_by(usuario=nombre_usuario).first()

    if user and check_password_hash(user.password, password):
      session['usuario'] = user.usuario
      flash('¡Inicio de sesión exitoso!', 'exito')
      return redirect(url_for('inicio'))
    else:
      flash('Usuario o contraseña incorrectos.', 'error')

  return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
  if request.method == 'POST':
    nombre_usuario = request.form.get('usuario')
    email = request.form.get('email')
    password = request.form.get('password')

    # Verificar si el usuario ya existe en MySQL
    user_existente = Usuario.query.filter_by(usuario=nombre_usuario).first()
    email_existente = Usuario.query.filter_by(email=email).first()

    if user_existente or email_existente:
      flash('El nombre de usuario o correo ya están registrados.', 'error')
    else:
      hashed_password = generate_password_hash(password)
      nuevo_usuario = Usuario(
          usuario=nombre_usuario, email=email, password=hashed_password
      )

      db.session.add(nuevo_usuario)
      db.session.commit()

      flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'exito')
      return redirect(url_for('login'))

  return render_template('registro.html')


@app.route('/inicio')
def inicio():
  if 'usuario' not in session:
    flash('Por favor inicia sesión para acceder a esta página.', 'error')
    return redirect(url_for('login'))

  return render_template('inicio.html', usuario=session['usuario'])


@app.route('/logout')
def logout():
  session.pop('usuario', None)
  flash('Has cerrado sesión correctamente.', 'exito')
  return redirect(url_for('login'))


if __name__ == '__main__':
  app.run(debug=True)