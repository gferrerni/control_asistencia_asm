# Control de Asistencia

Aplicación web simple para controlar la asistencia de socios a un evento.

## Ejecución con Docker

Esta aplicación está preparada para ser ejecutada fácilmente usando Docker, lo que elimina la necesidad de instalar dependencias o configurar entornos Python.

### Requisitos

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (incluido en Docker Desktop para Windows y Mac)

### Pasos para ejecutar la aplicación

1. **Clonar el repositorio:**

```bash
git clone https://github.com/tu-usuario/control-asistencia.git
cd control-asistencia
```

2. **Iniciar la aplicación:**

```bash
docker-compose up -d
```

3. **Acceder a la aplicación:**

Abre en tu navegador: http://localhost:5000

Para acceder desde otros dispositivos en la misma red, usa la IP del servidor en lugar de localhost.

### Comandos útiles

**Ver los logs de la aplicación:**
```bash
docker-compose logs -f
```

**Detener la aplicación:**
```bash
docker-compose down
```

**Reconstruir la aplicación después de cambios:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

**Ver el estado de los contenedores:**
```bash
docker-compose ps
```

### Estructura de datos

La aplicación usa un archivo CSV para almacenar los datos de los socios. Este archivo se mantiene persistente fuera del contenedor mediante un volumen Docker.

### Acceso desde dispositivos móviles

Como la aplicación se ejecuta en un contenedor accesible desde la red, cualquier dispositivo en la misma red puede acceder usando la IP del servidor:

http://[IP-del-servidor]:5000

### Vista para proyector

Para eventos en los que se requiera mostrar el estado de asistencia en un proyector, se puede acceder a la vista especial:

http://[IP-del-servidor]:5000/proyector 