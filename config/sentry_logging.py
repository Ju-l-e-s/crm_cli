import logging
import os
from dotenv import load_dotenv

import sentry_sdk
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk import add_breadcrumb

# Load environment variables from .env if available
load_dotenv()

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """Start Sentry if a DSN is set and it's not disabled."""
    if os.getenv("DISABLE_SENTRY") == "1":
        logger.debug("Sentry is disabled via DISABLE_SENTRY.")
        return

    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        logger.debug("No SENTRY_DSN found; Sentry will not start.")
        return

    if sentry_init is None:
        logger.warning("sentry-sdk package is missing; cannot start Sentry.")
        return

    # Send INFO logs as breadcrumbs, ERROR and above as events
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

    sentry_init(
        dsn=dsn,
        integrations=[sentry_logging, SqlalchemyIntegration()],
        send_default_pii=False,
        environment=os.getenv("APP_ENV", "dev"),
        traces_sample_rate=1.0,  # capture 100% of traces (adjust in prod)
    )

    logger.info("Sentry started successfully.")


def capture_event(message: str, level: str = "info", **tags) -> None:
    """
    Send a custom message to Sentry with custom tags and a breadcrumb.

    :param message: Message to send to Sentry.
    :param level: Severity level ('info', 'warning', 'error', etc.).
    :param tags: Additional tags (e.g., contract_id=..., user_id=...).
    """
    if (
        sentry_sdk.get_client() is None
        or os.getenv("DISABLE_SENTRY") == "1"
        or not os.getenv("SENTRY_DSN")
    ):
        logger.debug("Sentry is inactive; event '%s' not sent.", message)
        return

    try:
        add_breadcrumb(
            category="custom.event",
            message=message,
            level=level
        )
        with sentry_sdk.new_scope() as scope:
            for key, value in tags.items():
                scope.set_tag(key, value)
            sentry_sdk.capture_message(message, level=level)
    except Exception as exc:
        logger.error("Failed to send event to Sentry: %s", exc)
