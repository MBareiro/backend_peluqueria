from app import app, db
from models.usuario_model import Usuario
from flask import request, jsonify
from datetime import datetime, timedelta
import secrets
from flask_mail import Message # Asegúrate de que hayas configurado Flask-Mail previamente
from flask_mail import Message
from controllers.email_controller import *
import bcrypt
""" app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///horarios.db' """

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    # Obtén el correo electrónico proporcionado en la solicitud
    email = request.json.get('email')
    # Verifica si el correo electrónico existe en la base de datos
    user = Usuario.query.filter_by(email=email).first()
    if user:
        # Establece una fecha de vencimiento (por ejemplo, 24 horas después de la generación)
        expiration_time = datetime.utcnow() + timedelta(hours=24)
        # Genera un token único
        reset_token = generate_unique_token()
        # Almacena el token en el modelo de usuario
        user.reset_password_token = reset_token        
        user.reset_password_expiration = expiration_time
        db.session.commit()
        # Envia un correo electrónico al usuario con el enlace de restablecimiento
        subject = 'Restablecer Contraseña'
        sender = 'noreply@example.com'
        recipients = [email]
        reset_link = f'https://turnopro-frontend.web.app/reset-password/{reset_token}'  # Reemplaza con tu dominio
        """ reset_link = f'http://localhost:4200/reset-password/{reset_token}' """  # Reemplaza con tu dominio
        message = Message(subject=subject, sender=sender, recipients=recipients)
        message.body = f'Para restablecer tu contraseña, sigue este enlace: {reset_link}'        
        try:
            mail.send(message)
            return jsonify({'message': '*Se ha enviado un correo electrónico con las instrucciones para restablecer la contraseña.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'message': 'Correo electrónico no encontrado.'}), 404

# Función para generar un token único (debes implementarla)
def generate_unique_token():
    # Genera un token único seguro de 32 bytes
    return secrets.token_hex(16)

""" @app.route('/forgot-password/<token>', methods=['GET'])
def reset_password_with_token(token):
    # Implementa la lógica para verificar y procesar el token aquí
    # Luego, redirige al front-end con el token en la URL
    return redirect(f'http://localhost:4200/reset-password?token={token}', code=302)
 """
@app.route('/reset-password/<token>', methods=['POST'])
def process_reset_password(token):
    # Verifica que el token sea válido y no haya expirado
    user = Usuario.query.filter_by(reset_password_token=token).first()
    if user and user.reset_password_expiration > datetime.utcnow():        
        # Procesa el formulario y actualiza la contraseña
        new_password = request.json.get('new_password')
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password
        # Limpia el token y la fecha de vencimiento
        user.reset_password_token = None
        user.reset_password_expiration = None
        db.session.commit()
        return jsonify({'message': 'Contraseña restablecida con éxito. Puedes iniciar sesión con tu nueva contraseña.'}), 200
    else:
        return jsonify({'message': 'Token inválido o expirado. Por favor, solicita otro enlace de restablecimiento de contraseña.'}), 500
