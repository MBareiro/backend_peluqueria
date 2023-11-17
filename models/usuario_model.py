import datetime
import secrets
import bcrypt
from app import db, ma, app
from flask_login import UserMixin

class UsuarioSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nombre', 'apellido', 'direccion', 'telefono', 'password', 'email', 'role', 'active')


class Usuario(db.Model, UserMixin):

    reset_password_token = db.Column(db.String(100), unique=True)
    reset_password_expiration = db.Column(db.DateTime)
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)  # Asegura que el email sea único
    telefono = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, default=True)
    # Agrega la relación en la clase Usuario
    horarios = db.relationship('Horario', back_populates='usuario', lazy='dynamic')
    turnos = db.relationship('Appointment', back_populates='usuario')    
    dias_bloqueados = db.relationship('BlockedDay', back_populates='usuario')

    def __init__(self, nombre, apellido, direccion, password, email, telefono, role, active=True):
        self.nombre = nombre
        self.apellido = apellido
        self.direccion = direccion
        self.password = self.hash_password(password)  # Guarda la contraseña encriptada
        self.email = email
        self.telefono = telefono
        self.role = role
        self.active = active

        self.reset_password_token = None
        self.reset_password_expiration = None

    def generate_reset_password_token(self):
        self.reset_password_token = secrets.token_urlsafe(32)  # Generar un token seguro
        self.reset_password_expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Establecer una hora de vencimiento
        
    def hash_password(self, password):
        # Genera un salt aleatorio y hashea la contraseña
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        return hashed_password

    @classmethod
    def verificar_credenciales(cls, email, password):
        usuario = cls.query.filter_by(email=email).first()
        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario.password.encode('utf-8')):
            return usuario
        return None

with app.app_context():
    db.create_all()
