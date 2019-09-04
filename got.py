import argparse
import os
import hashlib
import zlib
from collections import namedtuple

# CLI arguments
ap = argparse.ArgumentParser()

args = ap.parse_args()

## Tuples and enums
IndexEntry = namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode',
    'uid', 'gid', 'size', 'sha1', 'flags', 'path',
])

## Helper functions
def init_repo(path):
    # Create the base path if needed
    os.mkdir(path)

    # Create .git path
    os.mkdir(os.path.join(path, '.git'))

    # Build each sub-path
    for sub_path in ['objects', 'refs', 'refs/heads']:
        os.mkdir(os.path.join(path, '.git', sub_path))

    # Build a HEAD file
    write_file(os.path.join(path, '.git', 'HEAD'),
               b'ref: refs/heads/master')

    print(f"Empty repo initalized in: {path}")


def hash_git_object(data, obj_type, do_write=True):
    # Build a file header
    file_header = f"{obj_type} {len(data)}".encode()

    # Join the header and file data
    file_data = file_header + b'\x00' + data

    # hash the file
    file_hash = hashlib.sha1(file_data).hexdigest()

    if do_write:
        # Get the file path to use
        file_path = os.path.join(
            '.git', 'objects', file_hash[:2], file_hash[2:])

        # Write the file if it does not already exist
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "r") as fp:
                fp.write(zlib.compress(file_data))
                fp.close()

    return file_hash

