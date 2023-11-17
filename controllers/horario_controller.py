from app import app, db
from models.horario_model import Horario, HorarioSchema
from flask import Flask, request, jsonify

from tenacity import retry, stop_after_attempt, wait_fixed
""" app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///horarios.db' """

horario_schema = HorarioSchema()
horarios_schema = HorarioSchema(many=True)
# Configura la estrategia de reintento
retry_strategy = retry(
    stop=stop_after_attempt(3),  # Intenta 3 veces como máximo
    wait=wait_fixed(2)  # Espera 5 segundos entre reintentos
)

@app.route('/guardar_horarios', methods=['POST'])
@retry_strategy
def guardar_horarios():
    data = request.json  # Recibe los datos del frontend
    for dia, horario_data in data.items():
        horario = Horario.query.filter_by(dia=dia, userId=horario_data['userId']).first()
        if horario:
            # Si el horario ya existe, actualiza los datos            
            horario.active_morning = horario_data['active_morning']
            horario.morning_start = horario_data['morning_start']
            horario.morning_end = horario_data['morning_end']
            horario.active_afternoon = horario_data['active_afternoon']
            horario.afternoon_start = horario_data['afternoon_start']
            horario.afternoon_end = horario_data['afternoon_end']
            horario.userId = horario_data['userId']
        else:
            # Si no existe, crea un nuevo horario
            new_horario = Horario(
                dia=dia,               
                active_morning=horario_data['active_morning'],
                morning_start=horario_data['morning_start'],
                morning_end=horario_data['morning_end'],
                active_afternoon=horario_data['active_afternoon'],
                afternoon_start=horario_data['afternoon_start'],
                afternoon_end=horario_data['afternoon_end'],
                userId = horario_data['userId']
            )
            db.session.add(new_horario)

    db.session.commit()
    return jsonify({'message': 'Horarios guardados exitosamente'})

@app.route('/obtener_horario_usuario/<user_id>', methods=['GET'])
@retry_strategy
def obtener_horario_usuario(user_id):
    horarios = Horario.query.filter_by(userId=user_id).all()
    horarios_data = {horario.dia: horario_schema.dump(horario) for horario in horarios}
    return jsonify(horarios_data)
