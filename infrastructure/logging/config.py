import structlog
import sys

def configure_logging() -> None:
    """Configure structured JSON logging as required by BSS-Core constitution Section 11."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    # Configure stdlib logging handler
    handler = structlog.stdlib.LoggerFactory().get_logger().handlers[0]
    if not handler.formatter:
        handler.setFormatter(structlog.dev.ConsoleRenderer())

    # Ensure all loggers use structured format
    for name in structlog.stdlogger.__dict__:
        logger = structlog.get_logger(name)
        logger.info("Logging configured per BSS-Core constitution Section 11")