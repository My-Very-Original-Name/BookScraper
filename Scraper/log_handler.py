import logging
import os

def setup_logging(run_id:str, log_dir:str, file_level, cleanup_old_logs:bool):
    if cleanup_old_logs: cleanup_logs()
    
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    active_log_dir = os.path.join(log_dir, ".activeRuns")
    if not os.path.exists(active_log_dir):
        os.mkdir(active_log_dir)
    log_path = os.path.join(active_log_dir, f"{run_id}.log")

    logger = logging.getLogger("scraper")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def cleanup_logs():
    pass