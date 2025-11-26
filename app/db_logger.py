# Importa el módulo estándar de logging de Python
import logging

# Importa el conector de MySQL
import mysql.connector

# Importa la clase de error específica de mysql.connector
from mysql.connector import Error


class MySQLHandler(logging.Handler):
    """
    Handler personalizado de logging que envía los registros (logs)
    a una tabla MySQL llamada 'logs'.

    Se espera una tabla con al menos las columnas:
      - logger (VARCHAR)
      - level (VARCHAR)
      - message (TEXT/VARCHAR)
      - pathname (TEXT/VARCHAR)
      - lineno (INT)
      - exception (TEXT/VARCHAR o NULL)
    """

    def __init__(self, db_config, level=logging.NOTSET):
        """
        Constructor del handler.

        :param db_config: diccionario con parámetros de conexión para mysql.connector.connect,
                          por ejemplo:
                          {
                              "host": "localhost",
                              "user": "usuario",
                              "password": "password",
                              "database": "nombre_bd"
                          }
        :param level: nivel mínimo de logging que manejará este handler.
        """
        # Llama al constructor de la clase base logging.Handler con el nivel indicado
        super().__init__(level)

        # Guarda la configuración de conexión a la base de datos
        self.db_config = db_config

        # Inicialmente la conexión es None (no hay conexión establecida)
        self.conn = None

        # Intenta establecer la conexión al crear el handler
        self._connect()

    def _connect(self):
        """
        Intenta establecer una conexión a la base de datos MySQL
        usando la configuración almacenada en self.db_config.
        """
        try:
            # Crea la conexión usando los parámetros del diccionario db_config
            self.conn = mysql.connector.connect(**self.db_config)
        except Error as e:
            # Si ocurre un error de MySQL, se imprime un mensaje en consola
            print(f"[MySQLHandler] Error de conexión: {e}")

    def emit(self, record: logging.LogRecord):
        """
        Método obligatorio en un Handler de logging.
        Es llamado por el sistema de logging cada vez que se emite un registro.

        :param record: instancia de logging.LogRecord con toda la información del log.
        """
        try:
            # Si no hay conexión o la conexión se ha cerrado, intenta reconectar
            if self.conn is None or not self.conn.is_connected():
                self._connect()

            # Si después de intentar reconectar seguimos sin conexión, salimos sin hacer nada
            if self.conn is None or not self.conn.is_connected():
                return

            # Crea un cursor para ejecutar consultas SQL
            cursor = self.conn.cursor()

            # Sentencia SQL para insertar un registro en la tabla logs
            # Se usan marcadores %s para valores parametrizados (evita inyección SQL)
            sql = """
                INSERT INTO logs (logger, level, message, pathname, lineno, exception)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            # Inicialmente no hay texto de excepción
            exc_text = None

            # Si el registro contiene información de excepción (por ejemplo, logger.exception())
            if record.exc_info:
                # Si el handler tiene un formatter configurado, usarlo para dar formato a la excepción
                if self.formatter:
                    exc_text = self.formatter.formatException(record.exc_info)
                else:
                    # Si no hay formatter definido, usar el formatter por defecto
                    exc_text = logging.Formatter().formatException(record.exc_info)

            # Prepara la tupla de datos que se insertará en la tabla
            # record.name      -> nombre del logger
            # record.levelname -> nivel en texto (INFO, ERROR, etc.)
            # record.getMessage() -> mensaje del log (con %s ya formateados)
            # record.pathname  -> ruta del archivo donde se generó el log
            # record.lineno    -> número de línea del archivo
            # exc_text         -> texto de la excepción formateada (o None)
            data = (
                record.name,
                record.levelname,
                record.getMessage(),
                record.pathname,
                record.lineno,
                exc_text,
            )

            # Ejecuta la sentencia SQL con los datos
            cursor.execute(sql, data)

            # Confirma la transacción para que el INSERT se guarde en la BD
            self.conn.commit()

            # Cierra el cursor (buena práctica para liberar recursos)
            cursor.close()

        except Error as e:
            # Si ocurre un error específico de MySQL al insertar el log, se muestra por consola
            print(f"[MySQLHandler] Error al insertar log: {e}")
        except Exception:
            # Si ocurre cualquier otra excepción, delega el manejo al mecanismo estándar
            # de logging (por ejemplo, imprime traceback, etc.)
            self.handleError(record)