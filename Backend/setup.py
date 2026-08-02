import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("enteka")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

for var, hint in {"SECRET_KEY": "Set a random string in Backend/.env",
                   "ALGORITHM": "Set to HS256 in Backend/.env",
                   "ACCESS_TOKEN_EXPIRE_MINUTES": "Set to a number (e.g. 30) in Backend/.env",
                   "MAX_UPLOAD_SIZE_MB": "Set to a number (e.g. 5) in Backend/.env"}.items():

    value = os.getenv(var)
    if not value:
        logger.critical("%s is not set. %s", var, hint)
        raise RuntimeError(f"{var} is not set. {hint}")

try:
    expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    if expire < 1:
        raise ValueError
except (ValueError, TypeError):
    logger.critical("ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer.")
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer.")

secret = os.getenv("SECRET_KEY")
if secret and secret in ("your-secret-key-here", "your-super-secret-key-change-in-production123"):
    logger.warning("SECRET_KEY is still a placeholder — change it before deployment.")