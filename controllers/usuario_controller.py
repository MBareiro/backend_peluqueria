import secrets
import string
from app import app, db
from models.usuario_model import Usuario, UsuarioSchema
from flask import jsonify, request
import bcrypt
from flask_login import login_user
from flask_login import login_required, logout_user
from controllers.email_controller import *

app.config['UPLOAD_FOLDER'] = '/img'

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

@app.route('/usuarios/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    print(email)
    print(password)
    if not email or not password:
        return jsonify({'message': 'Por favor, proporciona correo electrónico y contraseña'}), 400

    usuario = Usuario.verificar_credenciales(email, password)
    if usuario:
        login_user(usuario)  # Iniciar sesión al usuario
        return jsonify({'message': 'Inicio de sesión exitoso', 'usuario': usuario_schema.dump(usuario)})
    else:
        return jsonify({'message': 'Credenciales incorrectas'}), 401

@app.route('/usuarios/logout', methods=['POST'])
@login_required
def logout():
    logout_user()  # Cerrar la sesión del usuario
    return jsonify({'message': 'Sesión cerrada exitosamente'})


@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    all_usuarios = Usuario.query.all()
    result = usuarios_schema.dump(all_usuarios)
    return jsonify(result)


@app.route('/usuarios/<id>', methods=['GET'])
def get_usuario(id):
    usuario = Usuario.query.get(id)
    return usuario_schema.jsonify(usuario)


@app.route('/usuarios/<id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return usuario_schema.jsonify(usuario)


@app.route('/usuarios', methods=['POST'])
def create_usuario():
    nombre = request.json['nombre']
    apellido = request.json['apellido']
    direccion = request.json['direccion']
    email = request.json['email']  # Corregir esta línea
    telefono = request.json['telefono']
    role = request.json['role']

    password = generate_random_password()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        direccion=direccion,
        password=hashed_password,
        email=email,  # Corregir esta línea
        telefono=telefono,
        role=role
    )
    # Resto del código para enviar el correo y guardar el usuario en la base de datos

    print(password)
    print(email)
     # Enviar un correo electrónico al usuario
    msg = Message('Confirmación de turno', sender='tu_email@example.com', recipients=[email])
    msg.body = f'Su cuenta fue creada con éxito!\n\nEstas son sus credenciales.\nUsuario: {email}\nContraseña: {hashed_password}'
    
    # Envía el correo electrónico
    mail.send(msg)
    db.session.add(new_usuario)
    db.session.commit()
    
    return usuario_schema.jsonify(new_usuario)

@app.route('/usuarios/<id>', methods=['PUT'])
def update_usuario(id):
    # Obtén el usuario actual (puedes implementar tu lógica de autenticación aquí)   
    usuario = Usuario.query.get(id)
    if usuario is None:
        return jsonify({'message': 'Usuario no encontrado'})
    print(usuario.role)
    # Solo permite que se actualice el campo "role" si el usuario es un administrador
    if 'role' in request.json and usuario.role == 'admin':
        usuario.role = request.json['role']

    # Resto de las actualizaciones de campos
    usuario.nombre = request.json['nombre']
    usuario.apellido = request.json['apellido']
    usuario.email = request.json['email']
    usuario.telefono = request.json['telefono']
    usuario.active = request.json['active']

    db.session.commit()
    return usuario_schema.jsonify(usuario)



@app.route('/usuarios/change-password/<int:id>', methods=['POST'])
def change_password(id):
    # Retrieve the user by ID
    user = Usuario.query.get(id)
   
    if user is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    # Extract the passwords from the request
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    confirm_password = request.json.get('confirm_password')
    if(new_password != confirm_password):
        return jsonify({'error': 'Confirm password incorrect'}), 404
        
    # Check if the old password matches the stored password
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):        
        return jsonify({'message': 'Contraseña antigua incorrecta'}), 400
 
    # Generate hash for the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # Update the user's password with the hashed password
    user.password = hashed_password
    db.session.commit()

    return jsonify({'message': 'Contraseña cambiada exitosamente'}), 200

@app.route('/usuarios/activar/<int:id>', methods=['POST'])
def activar_usuario(id):
    # Obtén el usuario por su ID
    usuario = Usuario.query.get(id)

    # Verifica si el usuario existe
    if usuario is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    # Activa al usuario
    usuario.active = True
    db.session.commit()  # Guarda los cambios en la base de datos

    return jsonify({'message': 'Usuario activado exitosamente'}), 200


@app.route('/usuarios/desactivar/<int:id>', methods=['POST'])
def desactivar_usuario(id):
    # Obtén el usuario por su ID
    usuario = Usuario.query.get(id)

    # Verifica si el usuario existe
    if usuario is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    # Desactiva al usuario
    usuario.active = False
    db.session.commit()  # Guarda los cambios en la base de datos

    return jsonify({'message': 'Usuario desactivado exitosamente'}), 200


def hash_password(password):
    # Genera un salt aleatorio y hashea la contraseña
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

    
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password