import os
import shutil
import filecmp
import argparse
import time
import logging


def setup_logging(logfile):
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Create a fiel handler for the log file
    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create a console handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def sync_folders(source_path, replica_path):

    # Check if the source folder exists
    if not os.path.exists(source_path):
        logging.error(f"Source folder '{source_path}' does not exist.")
        return

    # Ensure the replica folder exists or create it
    if not os.path.exists(replica_path):
        os.makedirs(replica_path)

    # Sync files and subdirectories from source to replica
    for root, _, files in os.walk(source_path):
        relative_path = os.path.relpath(root, source_path)
        replica_root = os.path.join(replica_path, relative_path)

        # Ensure subdirectories exist in the replica folder
        for dir_name in os.listdir(root):
            source_dir = os.path.join(root, dir_name)
            replica_dir = os.path.join(replica_root, dir_name)

            if os.path.isdir(source_dir):
                if not os.path.exists(replica_dir):
                    os.makedirs(replica_dir)

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            # Check if the file exists in the replica folder and if it's different
            if not os.path.exists(replica_file) or not filecmp.cmp(source_file, replica_file, shallow=False):
                logging.info(f"Copying '{source_file}' to '{replica_file}'")
                shutil.copy2(source_file, replica_file)

    # Remove files and directories in replica that don't exist in source
    for root, dirs, files in os.walk(replica_path, topdown=False):
        relative_path = os.path.relpath(root, replica_path)
        source_root = os.path.join(source_path, relative_path)

        for dir_name in dirs:
            source_dir = os.path.join(source_root, dir_name)
            replica_dir = os.path.join(root, dir_name)

            if not os.path.exists(source_dir):
                logging.info(f"Removing directory '{replica_dir}'")
                os.rmdir(replica_dir)

        for file in files:
            source_file = os.path.join(source_root, file)
            replica_file = os.path.join(root, file)

            if not os.path.exists(source_file):
                logging.info(f"Removing file '{replica_file}'")
                os.remove(replica_file)

def main():

    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source_path", help="Source folder path")
    parser.add_argument("replica_path", help="Replica folder path")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval (in seconds)")
    parser.add_argument("log_file", help="Log file path")

    args = parser.parse_args()

    source_path = args.source_path
    replica_path = args.replica_path
    sync_interval = args.sync_interval
    log_file = args.log_file

    setup_logging(log_file)

    while True:
        sync_folders(source_path, replica_path)
        logging.info("Sync completed.")
        time.sleep(sync_interval)


if __name__ == "__main__":
    main()
