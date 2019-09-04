import argparse
import os
import hashlib
import zlib
from collections import namedtuple
import struct
import time

# CLI arguments
ap = argparse.ArgumentParser()

args = ap.parse_args()

## Tuples and enums
IndexEntry = namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode',
    'uid', 'gid', 'size', 'sha1', 'flags', 'path',
])

# Helper functions


def init_repo(path):
    """Create a new blank repo at specified path"""
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
    """Hash and optionally write an object"""
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
            with open(file_path, "w") as fp:
                fp.write(zlib.compress(file_data))
                fp.close()

    return file_hash


def read_git_index():
    # Attempt to load the index file
    try:
        with open(os.path.join('.git', 'index'), "r") as fp:
            file_data = fp.read()
            fp.close()
    except FileNotFoundError:
        # Return nothing if file not found
        return []

    # Verify the file signature
    file_digest = hashlib.sha1(file_data[:-20]).digest()
    assert digest == data[-20:], 'invalid index checksum'
    signature, version, num_entries = struct.unpack('!4sLL', data[:12])
    assert signature == b'DIRC', f"Index file signature is invalid: {signature}"
    assert version == 2, f"Index file version is unknown: {version}"

    # Get index entries
    index_entry_data = file_data[12:-20]
    index_entries = []
    while (i + 62) < len(file_entry_data):

        # Calculate field and path lengths
        field_len = i + 62
        path_len = entry_data.index(b'\x00', field_len)

        # Get current fields
        fields = struct.unpack(
            '!LLLLLLLLLL20sH', index_entry_data[i:field_len])

        # Get path
        path = entry_data[field_len:path_len]

        # Get current entry
        current_entry = IndexEntry(*(fields + (path.decode(),)))
        index_entries.append(current_entry)

        # Increment location
        i += ((62 + len(path) + 8) // 8) * 8

    assert len(entries) == num_entries
    return entries


def write_git_tree():
    # Load tree items
    tree_items = []
    for item in read_git_index():
        assert '/' not in item.path, "Currently, only TLDs are supported"
        mode_path = f"{item.mode} {item.path}".encode()
        tree_entry = mode_path + b'\x00' + item.sha1
        tree_items.append(tree_entry)

    return hash_object(b''.join(tree_items), 'tree')


def commit(message, author):
    tree = write_git_tree()

    with open(os.path.join('.git', 'refs', 'heads', 'master'), "r") as fp:
        parent = fp.read().strip()
        fp.close()
    
    # Gen metadata
    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone
    author_time = '{} {}{:02}{:02}'.format(
        timestamp,
        '+' if utc_offset > 0 else '-',
        abs(utc_offset) // 3600,
        (abs(utc_offset) // 60) % 60)
    
    # Build tree 
    lines = ['tree ' + tree]
    if parent:
        lines.append('parent ' + parent)
    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(author, author_time))
    lines.append('')
    lines.append(message)
    lines.append('')

    # Gen data
    data = '\n'.join(lines).encode()
    sha1 = hash_object(data, 'commit')
    master_path = os.path.join('.git', 'refs', 'heads', 'master')

    with open(master_path, "w") as fp:
        fp.write((sha1 + '\n').encode())
        fp.close()
    
    print('Committed to master: {:7}'.format(sha1))
    return sha1
