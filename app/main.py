# Importa el módulo estándar de logging de Python
import logging

# Importa el módulo os para leer variables de entorno
import os

# Importa el módulo time para hacer pausas (sleep)
import time

# Importa el handler personalizado que guarda logs en MySQL
from db_logger import MySQLHandler


def configure_logging():
    """
    Configura el sistema de logging:
      - Lee parámetros de conexión a la BD desde variables de entorno.
      - Crea un logger principal.
      - Añade un handler para consola.
      - Añade un handler para MySQL.
    Devuelve el logger configurado.
    """

    # Diccionario con la configuración de conexión a la base de datos.
    # Cada valor se obtiene de una variable de entorno, con un valor por defecto si no existe.
    db_config = {
        # Host de la base de datos. Por defecto "db" (útil en Docker con un servicio llamado 'db').
        "host": os.environ.get("DB_HOST", "db"),

        # Puerto de la base de datos. Se lee como texto y se convierte a int. Por defecto 3306.
        "port": int(os.environ.get("DB_PORT", "3306")),

        # Nombre de la base de datos. Por defecto "logging_demo".
        "database": os.environ.get("DB_NAME", "logging_demo"),

        # Usuario de la base de datos. Por defecto "appuser".
        "user": os.environ.get("DB_USER", "appuser"),

        # Contraseña del usuario de la base de datos. Por defecto "apppass".
        "password": os.environ.get("DB_PASSWORD", "apppass"),
    }

    # Obtiene (o crea) un logger con el nombre "demo-logger"
    logger = logging.getLogger("demo-logger")

    # Establece el nivel mínimo de este logger en INFO.
    # Esto significa que ignorará mensajes con nivel menor que INFO (por ejemplo DEBUG),
    # salvo que los handlers tengan niveles distintos.
    logger.setLevel(logging.INFO)

    # Crea un handler que envía los logs a la salida estándar (consola)
    console_handler = logging.StreamHandler()

    # El handler de consola tendrá nivel DEBUG, así que mostrará todos los mensajes
    # desde DEBUG hacia arriba.
    console_handler.setLevel(logging.DEBUG)

    # Define el formato de los mensajes de log:
    #   - %(asctime)s  -> fecha y hora
    #   - %(name)s     -> nombre del logger
    #   - %(levelname)s-> nivel del log (INFO, ERROR, etc.)
    #   - %(message)s  -> mensaje del log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Asigna el formatter al handler de consola para que use este formato al imprimir
    console_handler.setFormatter(formatter)

    # Añade el handler de consola al logger (ahora el logger ya escribe en consola)
    logger.addHandler(console_handler)

    # Crea el handler personalizado que envía los logs a MySQL
    # Se le pasa la configuración de BD y el nivel mínimo de log (INFO)
    db_handler = MySQLHandler(db_config=db_config, level=logging.INFO)

    # Usa el mismo formato de mensaje también para los registros que van a MySQL.
    # De esta forma, el texto del mensaje (message) tendrá el mismo estilo.
    db_handler.setFormatter(formatter)

    # Añade el handler de base de datos al logger (ahora el logger también escribe en MySQL)
    logger.addHandler(db_handler)

    # Devuelve el logger ya configurado con ambos handlers (consola + MySQL)
    return logger


def main():
    """
    Función principal de la demo:
      - Configura el logging.
      - Genera varios mensajes de log de diferentes niveles.
      - Simula una excepción para registrar el stack trace.
      - Entra en un bucle infinito enviando un 'heartbeat' cada 10 segundos.
    """

    # Obtiene el logger configurado (con handlers para consola y MySQL)
    logger = configure_logging()

    # Mensaje de INFO inicial para indicar que arranca la demo
    logger.info("Arrancando demo de logging a MySQL desde Docker 🚀")

    # Mensaje DEBUG que solo se verá en consola, porque:
    # - El logger tiene nivel INFO (no maneja DEBUG para otros handlers).
    # - Pero el console_handler está en DEBUG, así que sí lo muestra.
    logger.debug("Este DEBUG sólo se verá en consola.")

    # Mensaje INFO que:
    # - Se verá en consola (console_handler nivel DEBUG).
    # - Se guardará en MySQL (db_handler nivel INFO).
    logger.info("Este INFO se guarda en MySQL y se ve en consola.")

    # Mensaje WARNING de prueba
    logger.warning("Warning de prueba.")

    # Mensaje ERROR de prueba
    logger.error("Error de prueba!")

    # Bloque para provocar y registrar una excepción
    try:
        # Dividir 1 entre 0 genera ZeroDivisionError
        1 / 0
    except ZeroDivisionError:
        # logger.exception():
        # - Registra un mensaje con nivel ERROR.
        # - Incluye automáticamente la información de la excepción y el stack trace.
        logger.exception("Excepción de ejemplo (división entre cero).")

    # Contador para el heartbeat
    i = 0

    # Bucle infinito para enviar un 'heartbeat' periódico
    while True:
        # Registra un mensaje INFO con el número de heartbeat actual
        logger.info(f"Heartbeat #{i}")

        # Incrementa el contador de heartbeat
        i += 1

        # Espera 10 segundos antes del siguiente heartbeat
        time.sleep(10)


# Punto de entrada del script.
# Si este archivo se ejecuta directamente (python archivo.py),
# se llama a la función main().
if __name__ == "__main__":
    main()