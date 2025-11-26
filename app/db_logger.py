import logging
import mysql.connector
from mysql.connector import Error


class MySQLHandler(logging.Handler):
    def __init__(self, db_config, level=logging.NOTSET):
        super().__init__(level)
        self.db_config = db_config
        self.conn = None
        self._connect()

    def _connect(self):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"[MySQLHandler] Error de conexión: {e}")

    def emit(self, record: logging.LogRecord):
        try:
            if self.conn is None or not self.conn.is_connected():
                self._connect()

            if self.conn is None or not self.conn.is_connected():
                return

            cursor = self.conn.cursor()

            sql = """
                INSERT INTO logs (logger, level, message, pathname, lineno, exception)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            # Formatear la excepción si existe
            exc_text = None
            if record.exc_info:
                if self.formatter:
                    exc_text = self.formatter.formatException(record.exc_info)
                else:
                    exc_text = logging.Formatter().formatException(record.exc_info)

            data = (
                record.name,
                record.levelname,
                record.getMessage(),
                record.pathname,
                record.lineno,
                exc_text,
            )

            cursor.execute(sql, data)
            self.conn.commit()
            cursor.close()

        except Error as e:
            print(f"[MySQLHandler] Error al insertar log: {e}")
        except Exception:
            self.handleError(record)