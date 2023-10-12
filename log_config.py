from loguru import logger
import datetime, sys


logger.remove()

logger.level("critical", color="<red><bold>", icon="🛑", no=50)
logger.level("error", color="<red>", icon="❌", no=40)
logger.level("warning", color="<yellow>", icon="⚠️", no=30)
logger.level("success", color="<green>", icon="✅", no=25)
logger.level("info", color="", icon="ℹ️", no=20)
logger.level("debug", color="", icon="🐞", no=10)
logger.level("trace", color="", icon="🔍", no=5)

universal_format = "{file.path} | {time:YYYY-MM-DD at HH:mm:ss} | <level>{level: <8}</level> | {module}:{file}:{function}:{line} - <lvl>{message}</lvl>"

# replace termainal output format

today = datetime.datetime.now().strftime("%Y-%m-%d")

log_file_path = f"logs/{today}.log"
logger.add(log_file_path, rotation="1 day", level="TRACE", format=universal_format, compression="zip")
logger.add(sys.stderr, level="TRACE", format=universal_format, colorize=True)
