import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from models.appointment_model import Appointment, AppointmentSchema
from controllers.email_controller import *
from flask import jsonify

# Configura el planificador de tareas de fondo
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

def send_reminders():
    # Obtén la fecha de mañana
    tomorrow = datetime.now() + datetime.timedelta(days=1)
    formatted_date = tomorrow.strftime('%Y-%m-%d')

    # Filtra los turnos que tienen la fecha de mañana
    tomorrow_appointments = Appointment.query.filter_by(date=formatted_date).all()

    for appointment in tomorrow_appointments:
        send_reminder_email(appointment)  # Envia un correo de recordatorio para cada turno

    return jsonify({'message': 'Recordatorios enviados con éxito'}), 200

def send_reminder_email(appointment):
    # Aquí deberías implementar la lógica para enviar un correo de recordatorio al usuario
    # Puedes utilizar bibliotecas como Flask-Mail o cualquier otro servicio de correo electrónico.

    # Ejemplo usando Flask-Mail
    msg = Message('Recordatorio de turno', sender='tu_email@example.com', recipients=[appointment.email])
    msg.body = f'Tu turno está programado para mañana a las {appointment.selectedRadio}. ¡No olvides asistir!'
    mail.send(msg)

# Programa la tarea para ejecutarse un día antes del turno
def schedule_reminders():
    # Calcula la fecha actual
    today = datetime.now().date()
    # Programa la tarea para ejecutarse un día antes
    reminder_date = today + datetime.timedelta(days=1)
    scheduler.add_job(send_reminders, 'date', run_date=reminder_date)
