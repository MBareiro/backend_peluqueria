from app import app, db
from models.appointment_model import Appointment, AppointmentSchema
from flask import Flask, request, jsonify
from sqlalchemy import desc, asc  # Importa desc para el ordenamiento descendente
from datetime import datetime
from controllers.email_controller import *
from flask import Flask, request, render_template
from datetime import datetime
from dateutil import parser

""" app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///horarios.db' """

appointment_schema = AppointmentSchema()
appointment_schema = AppointmentSchema(many=True)

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



@app.route('/submit-form', methods=['POST'])
def submit_form():
    if not request.is_json:
        return jsonify({'message': 'Invalid request, JSON expected'}), 400     

    data = request.json
   # Obtener y formatear la fecha al formato adecuado
    date_str = data.get('date')
    date_obj = format_iso_date(date_str)

    if date_obj is None:
        return jsonify({'message': 'Fecha y hora no válidas'}), 400

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    phone_number = data.get('phoneNumber')
    peluquero = data.get('peluquero')   
    formatted_date = date_obj.strftime('%Y-%m-%d')
    schedule = data.get('schedule')
    selectedRadio = data.get('selectedRadio')

    # Create a new FormSubmission instance
    new_submission = Appointment(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        peluquero=peluquero,
        date=formatted_date,  # Use the formatted date
        schedule=schedule,
        selectedRadio=selectedRadio
    )

    # Add and commit to the database
    db.session.add(new_submission)
    db.session.commit()

    appointment_id = new_submission.id  # Obtén el ID del turno recién registrado
    """ cancel_url = f'http://localhost:4200/cancel-appointment/{appointment_id}' """
    cancel_url = f'https://turnopro-frontend.web.app/cancel-appointment/{appointment_id}'
    # Enviar un correo electrónico al usuario
    msg = Message('Turno registrado!', sender='tu_email@example.com', recipients=[email])
    msg.body = f'Tu turno ha sido registrado para el {formatted_date} a las {selectedRadio}. Si deseas cancelar tu turno, haz clic en el siguiente enlace: {cancel_url}'
    
    # Envía el correo electrónico
    mail.send(msg)
    return jsonify({'message': 'Form submitted successfully'}), 200

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
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Turno cancelado exitosamente'}), 200
    else:
        return jsonify({'message': 'No se encontró el turno'}), 404
 

@app.route('/get-specific-appointments/<selectedTime>/<selectedDate>/<peluqueroId>', methods=['GET'])
def get_specific_appointments(selectedTime, selectedDate, peluqueroId):
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

    return jsonify(filtered_appointments_serialized), 200
