"""
Input validation utilities for Joshua.

This module provides functions to validate and sanitize user input
to prevent security issues and ensure data integrity.
"""

import os
import re
import tarfile
from typing import Optional
from ..core.exceptions import JoshuaValidationError
from ..core.constants import (
    MAX_TARBALL_SIZE,
    UNSAFE_PATH_PATTERNS,
    K8S_MAX_LABEL_LENGTH
)


def validate_ensemble_id(ensemble_id: str) -> bool:
    """
    Validate ensemble ID format.
    
    Args:
        ensemble_id: Ensemble ID to validate
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> validate_ensemble_id("20230101-123456-username-abc123")
        True
    """
    if not ensemble_id:
        return False
    
    # Expected format: YYYYMMDD-HHMMSS-username-hash
    pattern = r'^[\d]{8}-[\d]{6}-[\w\-\.]+?-[\w]+$'
    return bool(re.match(pattern, ensemble_id))


def validate_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        JoshuaValidationError: If username is invalid
    """
    if not username:
        raise JoshuaValidationError("username", username, "Username cannot be empty")
    
    if len(username) > 27:  # Limit for K8s label compatibility
        raise JoshuaValidationError(
            "username", 
            username, 
            f"Username exceeds maximum length of 27 characters"
        )
    
    # Allow alphanumeric, dots, hyphens, underscores, and forward slashes
    pattern = r'^[\w\-\./]+$'
    if not re.match(pattern, username):
        raise JoshuaValidationError(
            "username",
            username,
            "Username contains invalid characters"
        )
    
    return True


def validate_tarball(tarball_path: str, max_size: int = MAX_TARBALL_SIZE) -> bool:
    """
    Validate tarball for security issues.
    
    Args:
        tarball_path: Path to tarball file
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid
        
    Raises:
        JoshuaValidationError: If tarball is invalid or unsafe
    """
    # Check file exists
    if not os.path.exists(tarball_path):
        raise JoshuaValidationError(
            "tarball",
            tarball_path,
            "File does not exist"
        )
    
    # Check file size
    file_size = os.path.getsize(tarball_path)
    if file_size > max_size:
        raise JoshuaValidationError(
            "tarball",
            tarball_path,
            f"File size {file_size} exceeds maximum {max_size}"
        )
    
    # Check for path traversal attempts
    try:
        with tarfile.open(tarball_path, 'r:gz') as tar:
            for member in tar.getmembers():
                if not check_archive_path(member.name):
                    raise JoshuaValidationError(
                        "tarball",
                        tarball_path,
                        f"Unsafe path in archive: {member.name}"
                    )
    except tarfile.TarError as e:
        raise JoshuaValidationError(
            "tarball",
            tarball_path,
            f"Invalid tarball format: {e}"
        )
    
    return True


def check_archive_path(name: str) -> bool:
    """
    Check if archive member path is safe.
    
    Args:
        name: Archive member name/path
        
    Returns:
        True if path is safe, False otherwise
    """
    path = os.path.normpath(name)
    
    # Check for absolute paths
    if path.startswith("/"):
        return False
    
    # Check for directory traversal
    if ".." in path:
        return False
    
    return True


def sanitize_path(path: str) -> Optional[str]:
    """
    Sanitize file paths to prevent directory traversal.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path or None if path is unsafe
        
    Example:
        >>> sanitize_path("../etc/passwd")
        None
        >>> sanitize_path("ensembles/test")
        'ensembles/test'
    """
    if not path:
        return None
    
    # Normalize the path
    clean_path = os.path.normpath(path)
    
    # Check for directory traversal attempts
    if '..' in clean_path:
        return None
    
    # Check for absolute paths
    if os.path.isabs(clean_path):
        return None
    
    return clean_path


def sanitize_for_file_name(name: str) -> str:
    """
    Sanitize string for use as a file name.
    
    Args:
        name: String to sanitize
        
    Returns:
        Sanitized string safe for use as filename
        
    Example:
        >>> sanitize_for_file_name('joshua/test')
        'joshua-test'
        >>> sanitize_for_file_name('joshua')
        'joshua'
    """
    if not name:
        return ""
    
    # Replace dangerous characters
    replacements = {
        '/': '-',
        '\\': '-',
        ':': '-',
        '*': '-',
        '?': '-',
        '"': '-',
        '<': '-',
        '>': '-',
        '|': '-',
        '\0': '-',
        '\n': '-',
        '\r': '-',
        '\t': '-',
    }
    
    result = name
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    
    # Remove leading/trailing dots and spaces
    result = result.strip('. ')
    
    # Limit length
    if len(result) > 255:
        result = result[:255]
    
    return result or "unnamed"


def validate_property_name(name: str) -> bool:
    """
    Validate property name.
    
    Args:
        name: Property name to validate
        
    Returns:
        True if valid
        
    Raises:
        JoshuaValidationError: If property name is invalid
    """
    if not name:
        raise JoshuaValidationError("property", name, "Property name cannot be empty")
    
    # Allow alphanumeric and underscores
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    if not re.match(pattern, name):
        raise JoshuaValidationError(
            "property",
            name,
            "Property name must start with letter/underscore and contain only alphanumeric/underscore"
        )
    
    return True


def validate_command(command: str) -> bool:
    """
    Validate command string for obvious security issues.
    
    Args:
        command: Command string to validate
        
    Returns:
        True if command appears safe
        
    Raises:
        JoshuaValidationError: If command contains dangerous patterns
    """
    if not command:
        return True  # Empty command is allowed
    
    # Check for obvious command injection attempts
    dangerous_patterns = [
        r';\s*rm\s+-rf',  # rm -rf attempts
        r'>\s*/dev/(sda|null)',  # Device overwrites
        r':(){ :|:& };:',  # Fork bomb
        r'`[^`]*`',  # Backtick command substitution
        r'\$\([^)]*\)',  # $() command substitution
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            raise JoshuaValidationError(
                "command",
                command,
                f"Command contains potentially dangerous pattern: {pattern}"
            )
    
    return True


def validate_seed(seed: any) -> int:
    """
    Validate and convert seed to integer.
    
    Args:
        seed: Seed value to validate
        
    Returns:
        Valid seed as integer
        
    Raises:
        JoshuaValidationError: If seed is invalid
    """
    try:
        seed_int = int(seed)
        if seed_int < 0 or seed_int >= 2**63:
            raise JoshuaValidationError(
                "seed",
                seed,
                "Seed must be between 0 and 2^63-1"
            )
        return seed_int
    except (ValueError, TypeError) as e:
        raise JoshuaValidationError(
            "seed",
            seed,
            f"Seed must be an integer: {e}"
        )