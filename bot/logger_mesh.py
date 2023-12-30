import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

log_file = 'bot.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
