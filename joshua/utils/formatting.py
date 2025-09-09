"""
Formatting utilities for Joshua.

This module provides functions for formatting and parsing various data types
used throughout the Joshua system.
"""

import re
import datetime
from typing import Optional, Tuple
from ..core.constants import TIMESTAMP_FMT, DATE_FORMAT


# Regex patterns for parsing time deltas
TIMEDELTA_REGEX1 = re.compile(
    r"(?P<days>[-\d]+) day[s]*, (?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d[\.\d+]*)"
)
TIMEDELTA_REGEX2 = re.compile(
    r"(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d[\.\d+]*)"
)


def format_ensemble(ensemble_id: str, properties: dict) -> str:
    """
    Format ensemble information for display.
    
    Args:
        ensemble_id: Ensemble identifier
        properties: Ensemble properties dictionary
        
    Returns:
        Formatted ensemble string
        
    Example:
        >>> format_ensemble("test-123", {"user": "alice", "status": "running"})
        '  test-123                                          status=running user=alice'
    """
    # Format properties as key=value pairs
    prop_str = " ".join(f"{k}={v}" for k, v in sorted(properties.items()))
    
    # Left-align ensemble ID with padding
    return f"  {ensemble_id:<50} {prop_str}"


def format_datetime(dt: datetime.datetime) -> str:
    """
    Format datetime object to standard string format.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted datetime string
        
    Example:
        >>> dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        >>> format_datetime(dt)
        '20230101-123045'
    """
    if dt is None:
        return ""
    return dt.strftime(TIMESTAMP_FMT)


def parse_datetime(dt_str: str) -> datetime.datetime:
    """
    Parse datetime string to datetime object.
    
    Args:
        dt_str: Datetime string in standard format
        
    Returns:
        Datetime object with UTC timezone
        
    Example:
        >>> parse_datetime("20230101-123045")
        datetime.datetime(2023, 1, 1, 12, 30, 45, tzinfo=datetime.timezone.utc)
    """
    if not dt_str:
        return None
    
    dt = datetime.datetime.strptime(dt_str, TIMESTAMP_FMT)
    return dt.replace(tzinfo=datetime.timezone.utc)


def format_timedelta(td: datetime.timedelta) -> str:
    """
    Format timedelta object to readable string.
    
    Args:
        td: Timedelta object
        
    Returns:
        Formatted timedelta string
        
    Example:
        >>> td = datetime.timedelta(days=1, hours=2, minutes=30)
        >>> format_timedelta(td)
        '1 day, 2:30:00'
    """
    if td is None:
        return ""
    
    # Remove microseconds for cleaner output
    return str(td).split(".", 2)[0]


def parse_timedelta(td_str: str) -> datetime.timedelta:
    """
    Parse timedelta string to timedelta object.
    
    Args:
        td_str: Timedelta string
        
    Returns:
        Timedelta object
        
    Example:
        >>> parse_timedelta("1 day, 2:30:00")
        datetime.timedelta(days=1, seconds=9000)
    """
    if not td_str:
        return None
    
    # Try parsing with days
    if "day" in td_str:
        match = TIMEDELTA_REGEX1.match(td_str)
    else:
        match = TIMEDELTA_REGEX2.match(td_str)
    
    if not match:
        raise ValueError(f"Invalid timedelta format: {td_str}")
    
    # Convert matched groups to timedelta kwargs
    parse_info = {key: float(val) for key, val in match.groupdict().items()}
    return datetime.timedelta(**parse_info)


def format_size(size_bytes: int, precision: int = 2) -> str:
    """
    Format byte size to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        precision: Number of decimal places
        
    Returns:
        Formatted size string
        
    Example:
        >>> format_size(1024)
        '1.00 KB'
        >>> format_size(1048576)
        '1.00 MB'
    """
    if size_bytes < 0:
        return "Invalid size"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.{precision}f} {units[unit_index]}"


def parse_size(size_str: str) -> int:
    """
    Parse human-readable size string to bytes.
    
    Args:
        size_str: Size string (e.g., "1.5 MB")
        
    Returns:
        Size in bytes
        
    Example:
        >>> parse_size("1.5 MB")
        1572864
        >>> parse_size("2 GB")
        2147483648
    """
    # Remove whitespace and convert to uppercase
    size_str = size_str.strip().upper()
    
    # Extract number and unit
    match = re.match(r'^([\d.]+)\s*([KMGTPE]?B?)$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    number = float(match.group(1))
    unit = match.group(2)
    
    # Unit multipliers
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
        'PB': 1024 ** 5,
        'K': 1024,
        'M': 1024 ** 2,
        'G': 1024 ** 3,
        'T': 1024 ** 4,
        'P': 1024 ** 5,
    }
    
    multiplier = multipliers.get(unit, 1)
    return int(number * multiplier)


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
        
    Example:
        >>> format_duration(3665)
        '1h 1m 5s'
        >>> format_duration(90)
        '1m 30s'
    """
    if seconds < 0:
        return "Invalid duration"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def format_result_code(code: int) -> str:
    """
    Format result code to human-readable string.
    
    Args:
        code: Result code
        
    Returns:
        Formatted result string
        
    Example:
        >>> format_result_code(0)
        'SUCCESS'
        >>> format_result_code(-2)
        'TIMEOUT'
    """
    result_map = {
        0: "SUCCESS",
        -1: "CANCELLED",
        -2: "TIMEOUT",
        -3: "STOPPED",
    }
    
    if code in result_map:
        return result_map[code]
    elif code > 0:
        return f"FAILURE({code})"
    else:
        return f"UNKNOWN({code})"


def format_percentage(value: float, total: float, precision: int = 1) -> str:
    """
    Format value as percentage of total.
    
    Args:
        value: Current value
        total: Total value
        precision: Number of decimal places
        
    Returns:
        Formatted percentage string
        
    Example:
        >>> format_percentage(25, 100)
        '25.0%'
    """
    if total == 0:
        return "N/A"
    
    percentage = (value / total) * 100
    return f"{percentage:.{precision}f}%"


def truncate_string(
    text: str,
    max_length: int,
    suffix: str = "..."
) -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
        
    Example:
        >>> truncate_string("This is a long string", 10)
        'This is...'
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def format_list(
    items: list,
    separator: str = ", ",
    max_items: Optional[int] = None
) -> str:
    """
    Format list of items for display.
    
    Args:
        items: List of items
        separator: Separator between items
        max_items: Maximum number of items to show
        
    Returns:
        Formatted list string
        
    Example:
        >>> format_list(['a', 'b', 'c', 'd', 'e'], max_items=3)
        'a, b, c... (and 2 more)'
    """
    if not items:
        return "[]"
    
    if max_items and len(items) > max_items:
        shown = items[:max_items]
        remaining = len(items) - max_items
        return f"{separator.join(map(str, shown))}... (and {remaining} more)"
    
    return separator.join(map(str, items))


def format_table(
    headers: list,
    rows: list,
    column_widths: Optional[list] = None
) -> str:
    """
    Format data as ASCII table.
    
    Args:
        headers: List of header strings
        rows: List of row data lists
        column_widths: Optional list of column widths
        
    Returns:
        Formatted table string
        
    Example:
        >>> headers = ['Name', 'Age']
        >>> rows = [['Alice', 30], ['Bob', 25]]
        >>> print(format_table(headers, rows))
        Name    Age
        -----   ---
        Alice   30
        Bob     25
    """
    if not headers:
        return ""
    
    # Calculate column widths if not provided
    if column_widths is None:
        column_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(cell)))
    
    # Format header
    header_line = "  ".join(
        str(h).ljust(w) for h, w in zip(headers, column_widths)
    )
    
    # Format separator
    separator_line = "  ".join("-" * w for w in column_widths)
    
    # Format rows
    row_lines = []
    for row in rows:
        row_line = "  ".join(
            str(cell).ljust(w) for cell, w in zip(row, column_widths)
        )
        row_lines.append(row_line)
    
    # Combine all parts
    return "\n".join([header_line, separator_line] + row_lines)


def parse_key_value_pairs(text: str) -> dict:
    """
    Parse key=value pairs from text.
    
    Args:
        text: Text containing key=value pairs
        
    Returns:
        Dictionary of parsed pairs
        
    Example:
        >>> parse_key_value_pairs("name=alice age=30 city='New York'")
        {'name': 'alice', 'age': '30', 'city': 'New York'}
    """
    pairs = {}
    
    # Match key=value pairs, handling quoted values
    pattern = r'(\w+)=([\'"]?)([^\'"]*)\2'
    matches = re.findall(pattern, text)
    
    for key, _, value in matches:
        pairs[key] = value
    
    return pairs