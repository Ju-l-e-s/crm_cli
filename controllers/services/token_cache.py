from pathlib import Path
import logging

logger = logging.getLogger(__name__)

TOKEN_PATH = Path.home() / ".epicevents_jwt"

def save_token(token: str, path: Path | None = None) -> None:
    """
    Save a JWT token to a specified file path.

    Args:
        token (str): The JWT token to save.
        path (Path | None): Optional custom path to save the token. Defaults to TOKEN_PATH.
    """
    if path is None:
        path = TOKEN_PATH
    try:
        with open(path, "w") as f:
            f.write(token)
    except OSError as e:
        logger.error(f"Failed to save token to {path}: {e}")

def load_token(path: Path | None = None) -> str | None:
    """
    Load a JWT token from a specified file path.

    Args:
        path (Path | None): Optional custom path to load the token from. Defaults to TOKEN_PATH.

    Returns:
        str | None: The token string if successful, None otherwise.
    """
    if path is None:
        path = TOKEN_PATH
    try:
        with open(path, "r") as f:
            token = f.read().strip()
            return token if token else None
    except FileNotFoundError:
        logger.warning(f"Token file not found at {path}.")
    except OSError as e:
        logger.error(f"Failed to load token from {path}: {e}")
    return None

def delete_token(path: Path | None = None) -> None:
    """
    Delete the JWT token from a specified file path.

    Args:
        path (Path | None): Optional custom path to delete the token from. Defaults to TOKEN_PATH.
    """
    if path is None:
        path = TOKEN_PATH
    try:
        path.unlink()
    except FileNotFoundError:
        logger.info(f"Token file already deleted or does not exist at {path}.")
    except OSError as e:
        logger.error(f"Failed to delete token at {path}: {e}")