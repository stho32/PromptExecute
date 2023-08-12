import hashlib
import csv
import os

CHECKSUM_FILE_HEADER = ['filepath', 'checksum']

def calculate_md5_checksum(file_path):
    """
    Calculate the md5 checksum of a file.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def detect_changes(file_path, checksums_file_path):
    """
    Detect if a file has changed by comparing its md5 checksum with a previously stored checksum.
    """
    checksum = calculate_md5_checksum(file_path)
    if not os.path.exists(checksums_file_path):
        return True
    with open(checksums_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['filepath'] == file_path:
                return row['checksum'] != checksum
    return True

def set_unchanged(file_path, checksums_file_path):
    """
    Set a file as unchanged by storing its md5 checksum.
    """
    checksum = calculate_md5_checksum(file_path)
    checksums = []
    if os.path.exists(checksums_file_path):
        with open(checksums_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            checksums = [row for row in csv_reader if row['filepath'] != file_path]
    checksums.append({'filepath': file_path, 'checksum': checksum})
    with open(checksums_file_path, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CHECKSUM_FILE_HEADER)
        writer.writeheader()
        writer.writerows(checksums)
