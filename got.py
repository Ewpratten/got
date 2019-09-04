import argparse
import os

# CLI arguments
ap = argparse.ArgumentParser()

args = ap.parse_args()

# Helper functions


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
