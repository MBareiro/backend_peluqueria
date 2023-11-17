from app import db
from app import app  # Asegúrate de importar app desde donde corresponde
from flask import request, jsonify
from models.bloqueo_model import BlockedDay
from dateutil import parser
from datetime import timedelta

def format_iso_date(date_str):
    try:
        date_obj = parser.parse(date_str)
        return date_obj
    except ValueError:
        return None

@app.route('/create-blocked-day-range', methods=['POST'])
def create_blocked_day_range():
    if not request.is_json:
        return jsonify({'message': 'Solicitud no válida, se esperaba JSON'}), 400

    data = request.json
    start_date = format_iso_date(data.get('start_date'))
    end_date = format_iso_date(data.get('end_date'))
    user_id = data.get('user_id')

    if not start_date or not end_date or user_id is None:
        return jsonify({'message': 'Los campos "start_date", "end_date" y "user_id" son obligatorios'}), 400

    # Crear una lista de fechas dentro del rango
    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    for date in date_range:
        # Verificar si ya existe un registro para esta fecha y usuario
        existing_blocked_day = BlockedDay.query.filter_by(user_id=user_id, blocked_date=date.strftime('%Y-%m-%d')).first()
        if not existing_blocked_day:
            # Si no existe, inserta un nuevo registro
            new_blocked_day = BlockedDay(user_id=user_id, blocked_date=date.strftime('%Y-%m-%d'))
            db.session.add(new_blocked_day)
        else:
            print(f"Registro existente para {date} y usuario {user_id}, no se insertará.")

    db.session.commit()

    return jsonify({'message': 'Días bloqueados con éxito'}, 201)


@app.route('/get-blocked-days/<int:user_id>', methods=['GET'])
def get_blocked_days(user_id):
    blocked_days = BlockedDay.query.filter_by(user_id=user_id).all()

    if not blocked_days:
        return jsonify({'message': 'No se encontraron días bloqueados para el usuario con user_id: {}'.format(user_id)}), 404

    blocked_days_serialized = [{'user_id': blocked_day.user_id, 'blocked_date': blocked_day.blocked_date} for blocked_day in blocked_days]
    return jsonify(blocked_days_serialized), 200

# Ruta para eliminar un día bloqueado
@app.route('/delete-blocked-day', methods=['DELETE'])
def delete_blocked_day():
    data = request.json
    user_id = data.get('user_id')
        
    if user_id is None:
        return jsonify({'message': 'El campo "user_id" es obligatorio'}), 400
    
    # Verificar si ya existen registros para este usuario
    existing_blocked_days = BlockedDay.query.filter_by(user_id=user_id).all()
    
    if not existing_blocked_days:
        return jsonify({'message': 'No se encontraron días bloqueados para el usuario'}), 404
    
    # Eliminar los registros existentes
    for blocked_day in existing_blocked_days:
        db.session.delete(blocked_day)
    
    db.session.commit()    
    return jsonify({'message': 'Días bloqueados eliminados con éxito'}, 200)
