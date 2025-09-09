"""
Filesystem utilities for Joshua.

This module provides safe filesystem operations with proper error handling
and atomic operations where needed.
"""

import os
import shutil
import tempfile
import glob
from pathlib import Path
from typing import Optional, List, Callable
from contextlib import contextmanager
from ..core.exceptions import JoshuaStorageError
from ..core.constants import DIR_TMP


def ensure_directory(path: str, mode: int = 0o755) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
        mode: Permission mode for new directories
        
    Returns:
        True if directory was created, False if it already existed
        
    Raises:
        JoshuaStorageError: If directory cannot be created
    """
    try:
        os.makedirs(path, mode=mode, exist_ok=True)
        return not os.path.exists(path)
    except OSError as e:
        raise JoshuaStorageError(f"Failed to create directory: {e}", path=path)


def clear_directory(path: str, preserve_dir: bool = True) -> None:
    """
    Clear all contents of a directory.
    
    Args:
        path: Directory path to clear
        preserve_dir: If True, keep the directory itself
        
    Raises:
        JoshuaStorageError: If directory cannot be cleared
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        if preserve_dir:
            os.makedirs(path, mode=0o755)
    except OSError as e:
        raise JoshuaStorageError(f"Failed to clear directory: {e}", path=path)


@contextmanager
def atomic_write(filepath: str, mode: str = 'w'):
    """
    Context manager for atomic file writes.
    
    Writes to a temporary file and moves it to the target location
    only if the write succeeds.
    
    Args:
        filepath: Target file path
        mode: File open mode
        
    Yields:
        File object for writing
        
    Example:
        >>> with atomic_write('/tmp/test.txt') as f:
        ...     f.write('content')
    """
    # Get directory and filename
    dirpath = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    
    # Ensure directory exists
    if dirpath:
        ensure_directory(dirpath)
    
    # Create temporary file in same directory (for atomic rename)
    temp_fd, temp_path = tempfile.mkstemp(
        prefix=f'.{basename}.',
        suffix='.tmp',
        dir=dirpath or '.'
    )
    
    try:
        with os.fdopen(temp_fd, mode) as temp_file:
            yield temp_file
            temp_file.flush()
            os.fsync(temp_file.fileno())
        
        # Atomic rename
        os.replace(temp_path, filepath)
        
    except Exception:
        # Clean up temporary file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def safe_remove(path: str) -> bool:
    """
    Safely remove a file or directory.
    
    Args:
        path: Path to remove
        
    Returns:
        True if removed, False if didn't exist
        
    Raises:
        JoshuaStorageError: If removal fails
    """
    try:
        if os.path.isfile(path):
            os.unlink(path)
            return True
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return True
        return False
    except OSError as e:
        raise JoshuaStorageError(f"Failed to remove {path}: {e}", path=path)


def find_files_by_pattern(
    directory: str,
    pattern: str,
    recursive: bool = False
) -> List[str]:
    """
    Find files matching a pattern.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match
        recursive: If True, search recursively
        
    Returns:
        List of matching file paths
        
    Example:
        >>> find_files_by_pattern('/tmp', '*.log', recursive=True)
        ['/tmp/test.log', '/tmp/subdir/debug.log']
    """
    if not os.path.isdir(directory):
        return []
    
    if recursive:
        pattern = f'**/{pattern}'
        return glob.glob(os.path.join(directory, pattern), recursive=True)
    else:
        return glob.glob(os.path.join(directory, pattern))


def get_directory_size(path: str) -> int:
    """
    Get total size of a directory in bytes.
    
    Args:
        path: Directory path
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def cleanup_old_files(
    directory: str,
    max_age_seconds: int,
    pattern: str = '*'
) -> int:
    """
    Remove files older than specified age.
    
    Args:
        directory: Directory to clean
        max_age_seconds: Maximum age in seconds
        pattern: File pattern to match
        
    Returns:
        Number of files removed
    """
    import time
    
    removed_count = 0
    current_time = time.time()
    
    for filepath in find_files_by_pattern(directory, pattern):
        try:
            file_age = current_time - os.path.getmtime(filepath)
            if file_age >= max_age_seconds:
                os.unlink(filepath)
                removed_count += 1
        except OSError:
            # Skip files we can't remove
            pass
    
    return removed_count


@contextmanager
def temporary_directory(prefix: str = 'joshua_', cleanup: bool = True):
    """
    Context manager for temporary directory creation.
    
    Args:
        prefix: Directory name prefix
        cleanup: If True, remove directory on exit
        
    Yields:
        Path to temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield temp_dir
    finally:
        if cleanup and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def copy_tree(src: str, dst: str, symlinks: bool = False) -> None:
    """
    Copy entire directory tree.
    
    Args:
        src: Source directory
        dst: Destination directory
        symlinks: If True, copy symlinks as symlinks
        
    Raises:
        JoshuaStorageError: If copy fails
    """
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst, symlinks=symlinks)
    except OSError as e:
        raise JoshuaStorageError(f"Failed to copy tree from {src} to {dst}: {e}")


def walk_files(
    directory: str,
    file_filter: Optional[Callable[[str], bool]] = None
) -> List[str]:
    """
    Walk directory and return all file paths.
    
    Args:
        directory: Directory to walk
        file_filter: Optional filter function for files
        
    Returns:
        List of file paths
    """
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            if file_filter is None or file_filter(filepath):
                files.append(filepath)
    return files


def ensure_symlink(source: str, link_name: str) -> None:
    """
    Ensure a symlink exists, creating or updating as needed.
    
    Args:
        source: Source path for symlink
        link_name: Symlink path
        
    Raises:
        JoshuaStorageError: If symlink cannot be created
    """
    try:
        # Remove existing link if it points elsewhere
        if os.path.islink(link_name):
            if os.readlink(link_name) == source:
                return  # Already correct
            os.unlink(link_name)
        elif os.path.exists(link_name):
            raise JoshuaStorageError(
                f"Cannot create symlink, file exists: {link_name}",
                path=link_name
            )
        
        # Create the symlink
        os.symlink(source, link_name)
        
    except OSError as e:
        raise JoshuaStorageError(
            f"Failed to create symlink from {source} to {link_name}: {e}"
        )


def is_path_safe(path: str, base_dir: str) -> bool:
    """
    Check if a path is safe (within base directory).
    
    Args:
        path: Path to check
        base_dir: Base directory that should contain the path
        
    Returns:
        True if path is within base_dir
    """
    try:
        # Resolve both paths to absolute
        real_path = os.path.realpath(path)
        real_base = os.path.realpath(base_dir)
        
        # Check if path is within base
        return real_path.startswith(real_base + os.sep) or real_path == real_base
    except OSError:
        return False