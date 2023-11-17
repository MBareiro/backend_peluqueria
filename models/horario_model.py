from app import db, app, ma
class HorarioSchema(ma.Schema):
    class Meta:
        fields = ('id', 'dia', 'active_morning', 'morning_start', 'morning_end', 'active_afternoon', 'afternoon_start', 'afternoon_end', 'userId')

class Horario(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.Integer)
    active_morning = db.Column(db.Boolean)
    morning_start = db.Column(db.String(8))
    morning_end = db.Column(db.String(8))
    active_afternoon = db.Column(db.Boolean)
    afternoon_start = db.Column(db.String(8))
    afternoon_end = db.Column(db.String(8))
    userId = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', back_populates='horarios')    

    
with app.app_context():
    db.create_all()  # aqui crea todas las tablas

