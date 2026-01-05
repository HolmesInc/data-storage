import logging
import logging.config
from settings import LOGGING

# Configure logging based on settings
logging.config.dictConfig(LOGGING)

# Create a logger instance that can be imported and used across the project
logger = logging.getLogger(__name__)
