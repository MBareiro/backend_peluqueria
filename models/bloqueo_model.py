from app import db, app  # Asegúrate de importar db desde donde corresponde

class BlockedDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blocked_date = db.Column(db.Date, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', back_populates='dias_bloqueados')

    def __init__(self, blocked_date, user_id):
        self.blocked_date = blocked_date
        self.user_id = user_id
        
with app.app_context():
    db.create_all()