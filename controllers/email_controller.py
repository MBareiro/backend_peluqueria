from app import app
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP
app.config['MAIL_PORT'] = 587  # Puerto del servidor SMTP
app.config['MAIL_USE_TLS'] = True  # Usar TLS (True/False)
app.config['MAIL_USE_SSL'] = False  # Usar SSL (True/False)
app.config['MAIL_USERNAME'] = 'bareiromartin420@gmail.com'  # Tu dirección de correo
app.config['MAIL_PASSWORD'] = 'gfpf qugi pdmy qpwq'  # Tu contraseña
mail = Mail(app)