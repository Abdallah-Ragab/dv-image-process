from loguru import logger
import datetime, sys, os


logger.remove()

logger.level("critical", color="<red><bold>", icon="🛑", no=50)
logger.level("error", color="<red>", icon="❌", no=40)
logger.level("warning", color="<yellow>", icon="⚠️", no=30)
logger.level("success", color="<green>", icon="✅", no=25)
logger.level("info", color="", icon="ℹ️", no=20)
logger.level("debug", color="", icon="🐞", no=10)
logger.level("trace", color="", icon="🔍", no=5)

project_directory = os.path.abspath(os.path.dirname(__file__))
logger = logger.patch(lambda record: record["extra"].update(relpath= os.path.relpath(os.path.relpath(record['file'].path, project_directory))))
universal_format = "{extra[relpath]: <12} | {time:YYYY-MM-DD at HH:mm:ss} | <level>{level: <8}</level> | {name}:{function}:{line} - <lvl>{message}</lvl>"
today = datetime.datetime.now().strftime("%Y-%m-%d")

log_file_path = f"logs/{today}.log"
logger.add(log_file_path, rotation="1 day", level="TRACE", format=universal_format, compression="zip")
logger.add(sys.stdout, level="DEBUG", format=universal_format, colorize=True)
