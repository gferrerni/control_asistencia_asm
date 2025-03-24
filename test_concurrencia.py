#!/usr/bin/env python3
import requests
import time
import random
import threading
from datetime import datetime
import pandas as pd
import json

# Configuración
BASE_URL = "https://localhost:5000"  # Ajusta según tu configuración
NUM_THREADS = 50 # Número de hilos concurrentes
NUM_REQUESTS = 50  # Número total de peticiones por hilo
DELAY_MIN = 0.1  # Delay mínimo entre peticiones
DELAY_MAX = 0.5  # Delay máximo entre peticiones

# Estadísticas globales
total_requests = 0
successful_requests = 0
failed_requests = 0
error_types = {}
start_time = None
end_time = None

# Lock para sincronizar la escritura de estadísticas
stats_lock = threading.Lock()

def load_test_data():
    """Carga los datos de prueba desde el archivo CSV"""
    try:
        df = pd.read_csv('socios.csv')
        return df['valor_qr'].tolist()
    except Exception as e:
        print(f"Error al cargar datos de prueba: {e}")
        return []

def make_request(qr_code):
    """Realiza una petición a la API"""
    global total_requests, successful_requests, failed_requests
    
    try:
        # Simular un pequeño delay aleatorio
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        
        # Configurar la sesión para ignorar la verificación SSL
        session = requests.Session()
        session.verify = False  # Ignorar verificación SSL para certificados autofirmados
        
        # Realizar la petición
        response = session.post(
            f"{BASE_URL}/marcar_asistencia",
            data={'valor_qr': qr_code},
            timeout=5
        )
        
        with stats_lock:
            total_requests += 1
            if response.status_code == 200:
                successful_requests += 1
            else:
                failed_requests += 1
                error_msg = f"Error {response.status_code}"
                error_types[error_msg] = error_types.get(error_msg, 0) + 1
                
    except requests.exceptions.RequestException as e:
        with stats_lock:
            total_requests += 1
            failed_requests += 1
            error_msg = str(type(e).__name__)
            error_types[error_msg] = error_types.get(error_msg, 0) + 1

def worker(qr_codes):
    """Función que ejecuta cada hilo"""
    for _ in range(NUM_REQUESTS):
        qr_code = random.choice(qr_codes)
        make_request(qr_code)

def print_stats():
    """Imprime las estadísticas de la prueba"""
    duration = end_time - start_time
    requests_per_second = total_requests / duration
    
    print("\n=== Estadísticas de la Prueba de Concurrencia ===")
    print(f"Tiempo total: {duration:.2f} segundos")
    print(f"Total de peticiones: {total_requests}")
    print(f"Peticiones exitosas: {successful_requests}")
    print(f"Peticiones fallidas: {failed_requests}")
    print(f"Tasa de éxito: {(successful_requests/total_requests)*100:.2f}%")
    print(f"Peticiones por segundo: {requests_per_second:.2f}")
    
    if error_types:
        print("\nTipos de errores encontrados:")
        for error, count in error_types.items():
            print(f"- {error}: {count}")

def main():
    global start_time, end_time
    
    print("Iniciando prueba de concurrencia...")
    
    # Cargar datos de prueba
    qr_codes = load_test_data()
    if not qr_codes:
        print("No se pudieron cargar los datos de prueba. Abortando...")
        return
    
    # Crear y iniciar hilos
    threads = []
    start_time = time.time()
    
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=worker, args=(qr_codes,))
        threads.append(thread)
        thread.start()
    
    # Esperar a que todos los hilos terminen
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    # Imprimir resultados
    print_stats()

if __name__ == "__main__":
    main() 