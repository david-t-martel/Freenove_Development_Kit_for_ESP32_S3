#!/usr/bin/env python3

import hashlib
import os
from pathlib import Path

PROJECT_ROOT = "c:/codedev/auricleinc/freenove/esp32s3"
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
LIB_DIR = os.path.join(PROJECT_ROOT, "lib")
COMPONENTS_DIR = os.path.join(PROJECT_ROOT, "components")
MAIN_DIR = os.path.join(PROJECT_ROOT, "main")


def calculate_file_hash(file_path):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def find_duplicate_files():
    """Find duplicate files between source directories and new structure."""
    # Dictionary to store file hashes and paths
    file_hashes = {}
    duplicate_files = []

    # Map of component directories to process
    dirs_to_process = {
        MAIN_DIR: "main component",
    }

    # Add all component directories
    for component in os.listdir(COMPONENTS_DIR):
        component_path = os.path.join(COMPONENTS_DIR, component)
        if os.path.isdir(component_path):
            dirs_to_process[component_path] = f"{component} component"

    # First, hash all files in the new structure
    for dir_path, description in dirs_to_process.items():
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith((".c", ".cpp", ".h", ".hpp")):
                    file_path = os.path.join(root, file)
                    try:
                        file_hash = calculate_file_hash(file_path)
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append((file_path, description))
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    # Now check source directories for duplicates
    source_dirs = {SRC_DIR: "src directory", LIB_DIR: "library directory"}

    for src_dir, description in source_dirs.items():
        if not os.path.exists(src_dir):
            continue

        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith((".c", ".cpp", ".h", ".hpp")):
                    file_path = os.path.join(root, file)
                    try:
                        file_hash = calculate_file_hash(file_path)
                        if file_hash in file_hashes:
                            for new_path, new_desc in file_hashes[file_hash]:
                                duplicate_files.append(
                                    {
                                        "original": file_path,
                                        "duplicate": new_path,
                                        "orig_desc": description,
                                        "dup_desc": new_desc,
                                        "hash": file_hash,
                                    }
                                )
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    return duplicate_files


def generate_cleanup_script(duplicates):
    """Generate a backup and removal script for duplicates."""
    if not duplicates:
        return "echo No duplicate files found."

    # Generate a Windows batch script
    script = [
        "@echo off",
        "echo Creating backup directory...",
        "mkdir %TEMP%\\esp32s3_orig_files_backup",
        "",
    ]

    # Add commands to back up and remove each file
    for dup in duplicates:
        original = dup["original"].replace("/", "\\")  # Convert to Windows path
        rel_path = os.path.relpath(original, PROJECT_ROOT).replace("/", "\\")
        backup_dir = f"%TEMP%\\esp32s3_orig_files_backup\\{os.path.dirname(rel_path)}"

        script.extend(
            [
                f"echo Processing: {rel_path}",
                f'mkdir "{backup_dir}" 2>nul',
                f'copy "{original}" "{backup_dir}\\{os.path.basename(original)}"',
                f'del "{original}"',
            ]
        )

    script.extend(
        [
            "",
            "echo Cleanup complete. Original files backed up to %TEMP%\\esp32s3_orig_files_backup",
        ]
    )

    return "\n".join(script)


def main():
    print("Searching for duplicate files...")
    duplicates = find_duplicate_files()

    if not duplicates:
        print("No duplicate files found.")
        return

    print(f"Found {len(duplicates)} duplicate files:")
    for i, dup in enumerate(duplicates, 1):
        print(f"{i}. Original ({dup['orig_desc']}): {dup['original']}")
        print(f"   Duplicate ({dup['dup_desc']}): {dup['duplicate']}")
        print()

    # Generate cleanup script
    cleanup_script = generate_cleanup_script(duplicates)
    cleanup_path = os.path.join(PROJECT_ROOT, "cleanup_duplicates.bat")

    with open(cleanup_path, "w") as f:
        f.write(cleanup_script)

    print(f"Created cleanup script at: {cleanup_path}")
    print("Review this script carefully before running it.")
    print("It will back up original files to a temp directory before removing them.")


if __name__ == "__main__":
    main()
