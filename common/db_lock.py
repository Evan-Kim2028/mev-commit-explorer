import fcntl
import logging
import os

# Define a global lock file path within the shared volume
LOCKFILE_PATH = "/app/db/data/duckdb_lock"


def acquire_lock(file_path: str = LOCKFILE_PATH):
    """Acquire an exclusive lock on the specified file."""
    logging.debug(f"Attempting to acquire lock on: {file_path}")
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Open the file in append mode to prevent truncation
    lockfile = open(file_path, "a+")
    try:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        logging.debug(f"Lock acquired on: {file_path}")
    except Exception as e:
        logging.error(f"Failed to acquire lock on {file_path}: {e}")
        lockfile.close()
        raise
    return lockfile


def release_lock(lockfile):
    """Release the lock and close the lockfile."""
    try:
        fcntl.flock(lockfile, fcntl.LOCK_UN)
        logging.debug("Lock released.")
    except Exception as e:
        logging.error(f"Failed to release lock: {e}")
    finally:
        lockfile.close()
