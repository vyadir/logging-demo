import logging
import os
import time

from db_logger import MySQLHandler


def configure_logging():
    db_config = {
        "host": os.environ.get("DB_HOST", "db"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "database": os.environ.get("DB_NAME", "logging_demo"),
        "user": os.environ.get("DB_USER", "appuser"),
        "password": os.environ.get("DB_PASSWORD", "apppass"),
    }

    logger = logging.getLogger("demo-logger")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    db_handler = MySQLHandler(db_config=db_config, level=logging.INFO)
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)

    return logger


def main():
    logger = configure_logging()

    logger.info("Arrancando demo de logging a MySQL desde Docker 🚀")

    logger.debug("Este DEBUG sólo se verá en consola.")
    logger.info("Este INFO se guarda en MySQL y se ve en consola.")
    logger.warning("Warning de prueba.")
    logger.error("Error de prueba!")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Excepción de ejemplo (división entre cero).")

    i = 0
    while True:
        logger.info(f"Heartbeat #{i}")
        i += 1
        time.sleep(10)


if __name__ == "__main__":
    main()
