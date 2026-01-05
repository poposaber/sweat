import hashlib
import argparse
import os

def calculate_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_folder_sha256(folder_path: str) -> str:
    sha256_hash = hashlib.sha256()
    for root, dirs, files in os.walk(folder_path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate SHA-256 hash of a file.")
    parser.add_argument("--file_path", type=str, help="Path to the file to hash.")
    parser.add_argument("--is_folder", action="store_true", help="Indicates if the path is a folder.")
    args = parser.parse_args()
    
    if args.is_folder:
        file_hash = calculate_folder_sha256(args.file_path)
    else:
        file_hash = calculate_sha256(args.file_path)
    print(f"SHA-256: {file_hash}")