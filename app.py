from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
login_manager = LoginManager(app)
login_manager.login_view = "login"
CORS(app)

# Configurar la base de datos
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/proyecto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://uflypegeltymsqap:aaKDW1KAY039djDeFOFy@b1jw7nqavnggowznnlg4-mysql.services.clever-cloud.com:3306/b1jw7nqavnggowznnlg4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate()
migrate.init_app(app, db) 
# Define las rutas utilizando el controlador de usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def hello():
    return jsonify(message='¡Hola mundo!')

#Comentar en pythonanywhere
""" from controllers.usuario_controller import *
from controllers.horario_controller import *
from controllers.appointment import * """
from controllers.reset_password import *

# Descomentar en pythonanywhere 

from controllers import usuario_controller, horario_controller, appointment_controller
app.route('/usuarios', methods=['GET'])(usuario_controller.get_usuarios)
app.route('/usuarios/<id>', methods=['GET'])(usuario_controller.get_usuario)
app.route('/usuarios/<id>', methods=['DELETE'])(usuario_controller.delete_usuario)
app.route('/usuarios', methods=['POST'])(usuario_controller.create_usuario)
app.route('/usuarios/<id>', methods=['PUT'])(usuario_controller.update_usuario)
app.route('/usuarios/login', methods=['POST'])(usuario_controller.login)

app.route('/obtener_horario_usuario/<user_id>', methods=['GET'])(horario_controller.obtener_horario_usuario)
app.route('/guardar_horarios', methods=['POST'])(horario_controller.guardar_horarios)

app.route('/get-appointments', methods=['GET'])(appointment_controller.get_appointments)
app.route('/get-morning-appointments', methods=['GET'])(appointment_controller.get_appointments)
app.route('/get-selected-appointments/<selectedTime>/<peluqueroId>/<selectedDate>', methods=['GET'])(appointment_controller.get_selected_appointments)
app.route('/submit-form', methods=['POST'])(appointment_controller.submit_form)
app.route('/cancel-appointment/<appointment_id>', methods=['DELETE'])(appointment_controller.cancel_appointment)
app.route('/get-specific-appointments/<selectedTime>/<selectedDate>/<peluqueroId>', methods=['GET'])(appointment_controller.get_specific_appointments)

if __name__ == '__main__':
    # ejecuta el servidor Flask en el puerto 5000
    app.run(host='0.0.0.0')
