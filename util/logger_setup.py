import logging
from rich.logging import RichHandler

def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            RichHandler()
        ]
    )

    return logging.getLogger("strava-analysis")