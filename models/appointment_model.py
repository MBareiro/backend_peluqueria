from app import db, app, ma

class AppointmentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'peluquero', 'date', 'schedule', 'selectedRadio')


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    peluquero = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    date = db.Column(db.String(20))
    schedule = db.Column(db.String(20))
    selectedRadio = db.Column(db.String(10))
    usuario = db.relationship('Usuario', back_populates='turnos')

    def __init__(self, first_name, last_name, email, phone_number, peluquero, date, schedule, selectedRadio):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.peluquero = peluquero
        self.date = date
        self.schedule = schedule
        self.selectedRadio = selectedRadio
