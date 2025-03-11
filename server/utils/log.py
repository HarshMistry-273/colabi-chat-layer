import logging

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure logs are printed
formatter = logging.Formatter(
    "{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)  # Ensure logs appear
logger.addHandler(console_handler)