"""Minimal repro: secret files not available in Render Workflow
task instances.

Secret files mounted via env groups (or directly on the service)
are available at /etc/secrets/<filename> for web services and
background workers, but appear to be missing in ephemeral
Workflow task instances.

Expected: the secret file is readable at /etc/secrets/my_secret.json
Actual: the file does not exist / cannot be read
"""

import logging
import os

from render_sdk import Workflows

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Workflows(default_timeout=30, default_plan="starter")

SECRET_PATH = "/etc/secrets/my_secret.json"


@app.task(name="check_secret_file")
def check_secret_file() -> dict:
    """Check whether the mounted secret file is accessible."""

    # 1. Check env var
    gac = os.environ.get("MY_SECRET_PATH")
    logger.info("MY_SECRET_PATH env var = %s", gac)

    # 2. Check if file exists
    exists = os.path.exists(SECRET_PATH)
    logger.info("os.path.exists(%s) = %s", SECRET_PATH, exists)

    # 3. Try to read it
    readable = False
    error = None
    try:
        with open(SECRET_PATH) as f:
            content = f.read(10)
            readable = len(content) > 0
        logger.info("File is readable")
    except Exception as e:
        error = str(e)
        logger.info("Cannot read file: %s", e)

    return {
        "env_var": gac,
        "file_exists": exists,
        "file_readable": readable,
        "error": error,
    }


if __name__ == "__main__":
    app.start()
