
from datetime import datetime
import json
EVENTO_FILE = 'info_evento.json'


def verificar_fecha_hora_tope():
    """Verifica si se ha pasado la fecha y hora tope para registrar asistencia"""
    try:
        with open(EVENTO_FILE, 'r') as f:
            info_evento = json.load(f)
            fecha_tope = datetime.fromisoformat(info_evento.get('fecha_tope_asistencia'))
            ahora = datetime.now()
            es_valido = ahora <= fecha_tope
            return es_valido
    except Exception as e:
        # Si hay error al leer el archivo, NO permitimos el registro para garantizar seguridad
        return False  # Cambiado a False para ser estrictos en caso de error

print(verificar_fecha_hora_tope())