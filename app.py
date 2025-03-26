from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from threading import Lock
import csv
import os
import pandas as pd
from datetime import datetime
import time
import json
from filelock import FileLock

app = Flask(__name__, static_url_path='/static')

# Ruta al archivo CSV
CSV_FILE = 'socios.csv'
LOCK_FILE = 'socios.csv.lock'
EVENTO_FILE = 'info_evento.json'
with open(EVENTO_FILE, 'r') as f:
    INFO_EVENTO = json.load(f)
    FECHA_INICIO = datetime.fromisoformat(INFO_EVENTO.get('fecha_evento'))
    FECHA_TOPE = datetime.fromisoformat(INFO_EVENTO.get('fecha_tope_asistencia'))
lock = Lock()

def leer_csv():
    """Lee el archivo CSV y devuelve un DataFrame con manejo de concurrencia"""
    with FileLock(LOCK_FILE, timeout=10):
        if os.path.exists(CSV_FILE):
            return pd.read_csv(CSV_FILE)
        return pd.DataFrame(columns=['valor_qr', 'numero_socio', 'nombre', 'apellidos', 'deudas', 'asiste'])

def guardar_csv(df):
    """Guarda el DataFrame en el archivo CSV con manejo de concurrencia"""
    with FileLock(LOCK_FILE, timeout=10):
        df.to_csv(CSV_FILE, index=False)

def verificar_fecha_hora_tope(ahora):
    """Verifica si se ha pasado la fecha y hora tope para registrar asistencia"""
    try:
        return ahora >= FECHA_INICIO and ahora < FECHA_TOPE
    except Exception as e:
        # Si hay error al leer el archivo, NO permitimos el registro para garantizar seguridad
        return False  # Cambiado a False para ser estrictos en caso de error

@app.route('/')
def index():
    """Página principal con el formulario de búsqueda"""
    df = leer_csv()
    # Contamos los asistentes
    asistentes = df[df['asiste'] == 1].shape[0]
    total = df.shape[0]
    
    # Verificar si hay errores en la solicitud anterior
    error = request.args.get('error', '')
    
    return render_template('index.html', asistentes=asistentes, total=total, error=error)

@app.route('/buscar', methods=['POST'])
def buscar_socio():
    """Busca un socio por número y muestra sus datos"""
    query = request.form.get('query', '')
    
    if not query:
        return redirect(url_for('index', error='Ingrese un número de socio o código QR'))
    
    df = leer_csv()
    
    # Intentar buscar por número de socio si es un número
    if query.isdigit():
        socio = df[df['numero_socio'] == int(query)]
    else:
        # Si no es un dígito, buscar por código QR
        socio = df[df['valor_qr'] == query]
    
    if socio.empty:
        return redirect(url_for('index', error=f'No se encontró socio con número o QR: {query}'))
    
    # Extraer datos del socio
    datos_socio = socio.iloc[0].to_dict()
    
    return render_template('socio.html', socio=datos_socio)

@app.route('/marcar_asistencia', methods=['POST'])
def marcar_asistencia():
    """Marca la asistencia de un socio"""
    with lock:
        # Verificar si se ha pasado la fecha y hora tope
        if not verificar_fecha_hora_tope(datetime.now()):
            return redirect(url_for('index', error='⚠️ REGISTRO DE ASISTENCIA CERRADO: Se ha superado la fecha y hora límite para registrar asistencia'))
        else:    
            # Aceptar tanto número de socio como valor_qr
            numero_socio = request.form.get('numero_socio', '')
            valor_qr = request.form.get('valor_qr', '')
            
            # Manejo de concurrencia para actualizar el CSV
            max_intentos = 5
            for intento in range(max_intentos):
                try:
                    df = leer_csv()
                    
                    # Buscar por número de socio o por valor_qr
                    if numero_socio and numero_socio.isdigit():
                        numero_socio = int(numero_socio)
                        # Verificar si el socio existe
                        if numero_socio not in df['numero_socio'].values:
                            return redirect(url_for('index', error=f'No se encontró socio con número {numero_socio}'))
                        
                        # Marcar asistencia por número de socio
                        df.loc[df['numero_socio'] == numero_socio, 'asiste'] = 1
                    elif valor_qr:
                        # Verificar si el QR existe
                        if valor_qr not in df['valor_qr'].values:
                            return redirect(url_for('index', error=f'No se encontró socio con QR {valor_qr}'))
                        
                        # Marcar asistencia por QR
                        df.loc[df['valor_qr'] == valor_qr, 'asiste'] = 1
                    else:
                        return redirect(url_for('index', error='Número de socio o QR inválido'))
                    
                    guardar_csv(df)
                    return redirect(url_for('index'))
                except Exception as e:
                    # Si hay error por bloqueo, esperar un poco y reintentar
                    if intento < max_intentos - 1:
                        time.sleep(0.5)  # Pequeña pausa antes de reintentar
                    else:
                        return redirect(url_for('index', error=f'Error al actualizar asistencia: {str(e)}'))
            
        return redirect(url_for('index'))

@app.route('/lista')
def lista():
    """Muestra la lista completa de socios"""
    df = leer_csv()
    fecha_actual = datetime.now()
    
    # Calcular totales
    total_socios = df.shape[0]
    total_presentes = df['asiste'].sum()
    total_ausentes = total_socios - total_presentes
    
    return render_template('lista.html', 
                         df=df, 
                         fecha_actual=fecha_actual,
                         total_socios=total_socios,
                         total_presentes=total_presentes,
                         total_ausentes=total_ausentes)

@app.route('/proyector')
def proyector():
    """Página optimizada para visualizar en un proyector"""
    df = leer_csv()
    asistentes = df[df['asiste'] == 1].shape[0]
    total = df.shape[0]
    return render_template('proyector.html', asistentes=asistentes, total=total)

@app.route('/reset_asistencia', methods=['POST'])
def reset_asistencia():
    #Reinicia todas las asistencias a 0
    max_intentos = 5
    for intento in range(max_intentos):
        try:
            df = leer_csv()
            df['asiste'] = 0
            guardar_csv(df)
            return redirect(url_for('index'))
        except Exception as e:
            if intento < max_intentos - 1:
                time.sleep(0.5)
            else:
                return redirect(url_for('index', error=f'Error al reiniciar asistencias: {str(e)}'))
    return redirect(url_for('index'))

@app.route('/api/socios', methods=['GET'])
def api_socios():
    """API para obtener la lista de socios en formato JSON"""
    df = leer_csv()
    return jsonify(df.to_dict('records'))

@app.route('/api/asistentes', methods=['GET'])
def api_asistentes():
    """API para obtener el número de asistentes y el total de socios"""
    df = leer_csv()
    asistentes = df[df['asiste'] == 1].shape[0]
    total = df.shape[0]
    return jsonify({
        'asistentes': asistentes,
        'total': total
    })

@app.route('/info_evento.json')
def get_info_evento():
    """Endpoint para servir el archivo info_evento.json"""
    #return send_from_directory('.', 'info_evento.json')
    return jsonify(INFO_EVENTO)
if __name__ == '__main__':
    ssl_context = ('certs/cert.pem', 'certs/key.pem')
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=ssl_context) 