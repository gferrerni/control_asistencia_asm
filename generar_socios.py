import random
import string
import csv

# Listas de nombres y apellidos para generar datos aleatorios
nombres = [
    "Juan", "María", "Carlos", "Ana", "Miguel", "Laura", "José", "Carmen", "Pedro", "Isabel",
    "Luis", "Sofía", "Antonio", "Elena", "Francisco", "Lucía", "Manuel", "Dolores", "Javier", "Pilar",
    "Alberto", "Raquel", "David", "Cristina", "Fernando", "Sara", "Alejandro", "Marta", "Daniel", "Patricia",
    "Pablo", "Silvia", "Sergio", "Beatriz", "Jorge", "Alicia", "Álvaro", "Andrea", "Diego", "Rocío",
    "Raúl", "Paula", "Víctor", "Nuria", "Jesús", "Clara", "Marcos", "Natalia", "Adrián", "Eva"
]

apellidos = [
    "García", "González", "Rodríguez", "Fernández", "López", "Martínez", "Sánchez", "Pérez", "Gómez", "Martín",
    "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Serrano", "Ramírez", "Molina", "Blanco",
    "Morales", "Suárez", "Ortega", "Delgado", "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Iglesias",
    "Medina", "Cortés", "Garrido", "Castillo", "Santos", "Lozano", "Guerrero", "Cano", "Prieto", "Méndez",
    "Cruz", "Flores", "Herrera", "Peña", "León", "Márquez", "Cabrera", "Gallego", "Calvo", "Vidal",
    "Campos", "Reyes", "Fuentes", "Nieto", "Caballero", "Pascual", "Ibáñez", "Hidalgo", "Carmona", "Ferrer"
]

# Generar datos aleatorios para 500 socios
socios = []
total_asistentes = 0
total_deudas = 0

for i in range(1, 501):
    # Generar QR con formato alfanumérico (letra + número)
    prefijo = random.choice(string.ascii_uppercase)
    if i < 10:
        valor_qr = f"{prefijo}00{i}"
    elif i < 100:
        valor_qr = f"{prefijo}0{i}"
    else:
        valor_qr = f"{prefijo}{i}"
    
    # Seleccionar nombres y apellidos aleatorios
    nombre = random.choice(nombres)
    apellido1 = random.choice(apellidos)
    apellido2 = random.choice(apellidos)
    apellidos_completo = f"{apellido1} {apellido2}"
    
    # Generar si tiene deudas (20% probabilidad)
    deudas = 1 if random.random() < 0.2 else 0
    total_deudas += deudas
    
    # Generar si asistió (30% probabilidad)
    asiste = 1 if random.random() < 0.3 else 0
    total_asistentes += asiste
    
    # Agregar socio a la lista
    socios.append([
        valor_qr,
        i,
        nombre,
        apellidos_completo,
        deudas,
        asiste
    ])

# Guardar a CSV usando la biblioteca estándar
with open("socios.csv", "w", newline="", encoding="utf-8") as archivo_csv:
    writer = csv.writer(archivo_csv)
    # Escribir encabezados
    writer.writerow(["valor_qr", "numero_socio", "nombre", "apellidos", "deudas", "asiste"])
    # Escribir datos
    writer.writerows(socios)

print(f"Se han generado 500 socios con datos aleatorios en socios.csv")
print(f"Total asistentes: {total_asistentes}")
print(f"Total con deudas: {total_deudas}")