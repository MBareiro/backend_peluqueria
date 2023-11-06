import random
from app import app, db
from models.appointment_model import Appointment, AppointmentSchema
from flask import Flask, request, jsonify
from sqlalchemy import desc, asc  # Importa desc para el ordenamiento descendente
from controllers.email_controller import *
from flask import Flask, request, render_template
from dateutil import parser
from dateutil.parser import parse
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
""" app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///horarios.db' """

appointment_schema = AppointmentSchema()
appointment_schema = AppointmentSchema(many=True)
confirmation_codes = {}

# Nueva ruta para obtener los turnos
@app.route('/get-appointments', methods=['GET'])
def get_appointments():
    # Obtiene todos los turnos desde la base de datos
    all_appointments = Appointment.query.all()
    appointments = appointment_schema.dump(all_appointments)
    return jsonify(appointments), 200

@app.route('/get-morning-appointments', methods=['GET'])
def get_morning_appointments():
    # Obtiene todos los turnos de la mañana desde la base de datos
    morning_appointments = Appointment.query.filter_by(schedule="morning").all()
    morning_appointments_serialized = appointment_schema.dump(morning_appointments)
    return jsonify(morning_appointments_serialized), 200

@app.route('/get-selected-appointments/<selectedTime>/<peluqueroId>/<selectedDate>', methods=['GET'])
def get_selected_appointments(selectedTime, peluqueroId, selectedDate):
    if selectedTime not in ['morning', 'afternoon']:
        return jsonify(message='Invalid selected time'), 400

    # Filtrar los turnos según el tiempo seleccionado (mañana o tarde)
    filtered_appointments = Appointment.query.filter_by(schedule=selectedTime, peluquero=peluqueroId, date=selectedDate)
    # Ordena los turnos según la columna selectedRadio en orden descendente
    filtered_appointments = filtered_appointments.order_by(asc(Appointment.selectedRadio))  # Corrección: usar 'desc' para ordenar descendente
    filtered_appointments = filtered_appointments.all()
    filtered_appointments_serialized = appointment_schema.dump(filtered_appointments)
    return jsonify(filtered_appointments_serialized), 200
    
# Ruta para confirmar el código de confirmación
@app.route('/confirm-appointment', methods=['POST'])
def confirm_appointment():
    if not request.is_json:
        return jsonify({'message': 'Invalid request, JSON expected'}), 400     

    data = request.json
    email = data.get('email')
    confirmation_code = data.get('code')

    if email in confirmation_codes and confirmation_codes[email] == confirmation_code:
        print("---------------------------")
        # El código de confirmación es válido, procede a registrar el turno
        del confirmation_codes[email]  # Elimina el código de confirmación
        return jsonify({'message': 'Código de confirmación correcto'}, 200)
    else:
        return jsonify({'message': 'Código de confirmación incorrecto'}, 400)

# Función para crear un turno
@app.route('/create-appointment', methods=['POST'])
def create_appointment():
    if not request.is_json:
        return jsonify({'message': 'Invalid request, JSON expected'}), 400     

    data = request.json
    date_str = data.get('date')
    date_obj = format_iso_date(date_str)

    if date_obj is None:
        return jsonify({'message': 'Fecha y hora no válidas'}, 400)
    
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    phone_number = data.get('phoneNumber')
    peluquero = data.get('peluquero')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    schedule = data.get('schedule')
    selectedRadio = data.get('selectedRadio')

    new_submission = Appointment(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        peluquero=peluquero,
        date=formatted_date,
        schedule=schedule,
        selectedRadio=selectedRadio
    )

    db.session.add(new_submission)
    db.session.commit()
    if(email):
        appointment_id = new_submission.id
        cancel_url = f'https://turnopro-frontend.web.app/cancel-appointment/{appointment_id}'    
        """ cancel_url = f'http://localhost:4200/cancel-appointment/{appointment_id}' """
        msg = Message('Turno registrado!', sender='tu_email@example.com', recipients=[email])
        msg.body = f'Tu turno ha sido registrado para el {formatted_date} a las {selectedRadio}. Si deseas cancelar tu turno (hasta un día antes del turno programado), haz clic en el siguiente enlace: {cancel_url}'
        mail.send(msg)    
    
    return jsonify({'message': 'Turno confirmado con éxito'}, 200)
    
def generate_confirmation_code():
    return str(random.randint(1000, 9999))

# Ruta para enviar un código de confirmación
@app.route('/send-confirmation-code', methods=['POST'])
def send_confirmation_code():
    if not request.is_json:
        return jsonify({'message': 'Invalid request, JSON expected'}), 400     

    data = request.json
    email = data.get('email')
    confirmation_code = generate_confirmation_code()
    confirmation_codes[email] = confirmation_code
    msg = Message('Código de confirmación', sender='tu_email@example.com', recipients=[email])
    msg.body = f'Tu código de confirmación es: {confirmation_code}'
    # Envía el correo electrónico con el código de confirmación
    mail.send(msg)
    return jsonify({'message': 'Código de confirmación enviado con éxito'}), 200


def format_iso_date(date_str):
    try:
        date_obj = parser.parse(date_str)
        return date_obj
    except ValueError:
        return None

@app.route('/cancel-appointment/<appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        # Obtén la fecha actual
        current_date = datetime.now().date()
        # Convierte la fecha del turno al formato datetime
        appointment_date = parse(appointment.date).date()
        # Calcula la diferencia de días entre la fecha actual y la fecha del turno
        days_difference = (appointment_date - current_date).days
        print(days_difference)
        # Verifica si la diferencia de días es mayor o igual a 1 (un día de anticipación)
        if days_difference > 1:
            print("netro")
            db.session.delete(appointment)
            db.session.commit()
            return jsonify({'message': 'Turno cancelado exitosamente'}), 200
        else:
            return jsonify({'message': 'No se puede cancelar el turno con menos de un día de anticipación'}), 400
    else:
        return jsonify({'message': 'No se encontró el turno'}), 404
 

# Configura la estrategia de reintento
retry_strategy = retry(
    stop=stop_after_attempt(3),  # Intenta 3 veces como máximo
    wait=wait_fixed(2)  # Espera 5 segundos entre reintentos
)

@app.route('/get-specific-appointments/<selectedTime>/<selectedDate>/<peluqueroId>', methods=['GET'])
@retry_strategy
def get_specific_appointments(selectedTime, selectedDate, peluqueroId):
    print(selectedTime)
    print(selectedDate)
    print(peluqueroId)
    # Convertir la fecha recibida a un objeto datetime
    try:
        selected_date_obj = datetime.strptime(selectedDate, '%a %b %d %Y %H:%M:%S GMT%z (hora estándar de Argentina)')
    except ValueError:
        return jsonify(message='Invalid date format'), 400

    # Formatear la fecha en el mismo formato que tienes en la base de datos
    formatted_selected_date = selected_date_obj.strftime('%Y-%m-%d')
    # Filtrar los turnos según el tiempo seleccionado (mañana o tarde) y la fecha
    filtered_appointments = Appointment.query.filter_by(schedule=selectedTime, peluquero=peluqueroId, date=formatted_selected_date)
    # Ordenar los turnos según la columna selectedRadio en orden descendente
    filtered_appointments = filtered_appointments.order_by(asc(Appointment.selectedRadio))
    # Seleccionar solo el campo 'selectedRadio' de los turnos
    filtered_appointments = filtered_appointments.with_entities(Appointment.selectedRadio).all()
    # Serializar los selectedRadios
    filtered_appointments_serialized = [item[0] for item in filtered_appointments]
    print(filtered_appointments_serialized)
    return jsonify(filtered_appointments_serialized), 200


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
    today = datetime.datetime.now().date()
    # Programa la tarea para ejecutarse un día antes
    reminder_date = today + datetime.timedelta(days=1)
    scheduler.add_job(send_reminders, 'date', run_date=reminder_date)
