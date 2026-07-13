import logging
import os


def setup_logger() -> logging.Logger:
    log_path = os.path.join(os.path.dirname(__file__), "pipeline_audit.log")

    logger = logging.getLogger("registration")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


def log_referral_result(logger, admin_id, action: str, patient_id: str = None, detail: str = ""):
    parts = [f"adminid={admin_id}", f"action={action}"]
    if patient_id:
        parts.append(f"patientid={patient_id}")
    if detail:
        parts.append(detail)
    msg = " | ".join(parts)

    if action == "FAILED":
        logger.error(msg)
    elif action == "SKIPPED_EXISTING":
        logger.warning(msg)
    else:
        logger.info(msg)
