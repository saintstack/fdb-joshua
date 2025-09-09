# Joshua Refactoring Guide

## Overview

This guide explains how to migrate the existing monolithic Joshua codebase to the new modular structure. The refactoring breaks down large files (1000+ lines each) into focused, reusable modules.

## Benefits of Refactoring

1. **Better Organization**: Code is organized by functionality rather than scattered across large files
2. **Improved Testability**: Smaller modules are easier to unit test
3. **Reduced Duplication**: Common utilities are centralized
4. **Better Error Handling**: Consistent exception hierarchy
5. **Easier Maintenance**: Developers can find and modify code more easily
6. **Type Safety**: Type hints throughout for better IDE support

## New Module Structure

```
joshua/
├── core/               # Core components
│   ├── config.py      # Centralized configuration
│   ├── constants.py   # All constants in one place
│   └── exceptions.py  # Custom exception hierarchy
├── utils/             # Reusable utilities
│   ├── validation.py  # Input validation functions
│   ├── filesystem.py  # Safe file operations
│   ├── logging.py     # Logging configuration
│   └── formatting.py  # Data formatting utilities
├── models/            # Data models (to be created)
├── storage/           # Storage abstraction (to be created)
└── agent/ → cli/      # Agent and CLI code (to be refactored)
```

## Migration Steps

### Step 1: Extract Common Utilities

**From `joshua_model.py` lines 186-209:**
```python
# OLD CODE
def format_timedelta(timedelta_obj):
    return str(timedelta_obj).split(".", 2)[0]

def format_datetime(dt_obj):
    return dt_obj.strftime(TIMESTAMP_FMT)
```

**NEW CODE:**
```python
from joshua.utils.formatting import format_timedelta, format_datetime
```

### Step 2: Replace Custom Exceptions

**From `joshua_agent.py` lines 63-72:**
```python
# OLD CODE
class JoshuaError(Exception):
    def __init__(self, msg):
        self.msg = msg
```

**NEW CODE:**
```python
from joshua.core.exceptions import JoshuaError, JoshuaTimeout
```

### Step 3: Centralize Configuration

**From scattered throughout files:**
```python
# OLD CODE
DEFAULT_TIMEOUT = 5400
BLOB_KEY_LIMIT = 8192
# ... scattered constants
```

**NEW CODE:**
```python
from joshua.core.config import config
from joshua.core.constants import DEFAULT_TIMEOUT, BLOB_KEY_LIMIT

# Access configuration
timeout = config.default_timeout
```

### Step 4: Use Validation Utilities

**From `joshua_agent.py` lines 157-164:**
```python
# OLD CODE
def sanitize_for_file_name(name):
    return "".join(a if a != "/" else "-" for a in name)
```

**NEW CODE:**
```python
from joshua.utils.validation import sanitize_for_file_name
```

### Step 5: Implement Safe File Operations

**From `joshua_agent.py` lines 295-302:**
```python
# OLD CODE
def clear_directory(path):
    try:
        shutil.rmtree(path)
        os.mkdir(path)
    except Exception as e:
        log(e)
```

**NEW CODE:**
```python
from joshua.utils.filesystem import clear_directory

# Use with proper error handling
try:
    clear_directory(path)
except JoshuaStorageError as e:
    logger.error(f"Failed to clear directory: {e}")
```

### Step 6: Set Up Proper Logging

**Throughout all files:**
```python
# OLD CODE
def log(outputText, newline=True):
    print(outputText, file=getFileHandle())
```

**NEW CODE:**
```python
from joshua.utils.logging import get_logger

logger = get_logger(__name__)
logger.info("Starting process")
logger.error("Error occurred", exc_info=True)
```

## Function Mapping

### joshua.py → Multiple Modules

| Old Function | New Module | New Function |
|-------------|------------|--------------|
| `format_ensemble()` | `utils.formatting` | `format_ensemble()` |
| `timestamp_of()` | `utils.formatting` | `parse_datetime()` |
| `get_username()` | `core.config` | `config.username` |

### joshua_agent.py → Multiple Modules

| Old Function | New Module | New Function |
|-------------|------------|--------------|
| `JoshuaError` | `core.exceptions` | `JoshuaError` |
| `sanitize_for_file_name()` | `utils.validation` | `sanitize_for_file_name()` |
| `check_archive_path()` | `utils.validation` | `check_archive_path()` |
| `clear_directory()` | `utils.filesystem` | `clear_directory()` |
| `ensure_state()` | Split into multiple functions |

### joshua_model.py → Multiple Modules

| Old Function | New Module | New Function |
|-------------|------------|--------------|
| Constants | `core.constants` | Various constants |
| `format_datetime()` | `utils.formatting` | `format_datetime()` |
| `format_timedelta()` | `utils.formatting` | `format_timedelta()` |
| `wrap_error()` | `storage.messaging` | `wrap_error()` (to be created) |

## Breaking Down Large Functions

### Example: Refactoring `run_ensemble()`

The original `run_ensemble()` function is 200+ lines. Break it down:

```python
# NEW STRUCTURE
class EnsembleRunner:
    def __init__(self, ensemble_id: str, config: JoshuaConfig):
        self.ensemble_id = ensemble_id
        self.config = config
        self.logger = get_logger(__name__)
    
    def run(self) -> int:
        """Main entry point."""
        try:
            self._validate_ensemble()
            self._prepare_environment()
            result = self._execute_test()
            self._cleanup()
            return result
        except Exception as e:
            self.logger.error(f"Ensemble failed: {e}")
            raise
    
    def _validate_ensemble(self):
        """Validate ensemble before running."""
        # Validation logic
    
    def _prepare_environment(self):
        """Set up execution environment."""
        # Environment setup
    
    def _execute_test(self) -> int:
        """Execute the actual test."""
        # Test execution
    
    def _cleanup(self):
        """Clean up after test."""
        # Cleanup logic
```

## Testing Strategy

### Unit Tests for New Modules

```python
# tests/test_utils_validation.py
import pytest
from joshua.utils.validation import validate_username, sanitize_path

def test_validate_username_valid():
    assert validate_username("alice") == True

def test_validate_username_too_long():
    with pytest.raises(JoshuaValidationError):
        validate_username("a" * 100)

def test_sanitize_path_safe():
    assert sanitize_path("data/file.txt") == "data/file.txt"

def test_sanitize_path_traversal():
    assert sanitize_path("../etc/passwd") is None
```

### Integration Tests

```python
# tests/integration/test_ensemble_lifecycle.py
def test_ensemble_complete_lifecycle():
    """Test creating, running, and stopping an ensemble."""
    config = JoshuaConfig()
    ensemble_id = create_test_ensemble()
    
    runner = EnsembleRunner(ensemble_id, config)
    result = runner.run()
    
    assert result == 0
    cleanup_test_ensemble(ensemble_id)
```

## Gradual Migration Plan

### Phase 1: Core Infrastructure (Week 1)
- [x] Create core modules (config, constants, exceptions)
- [x] Create utility modules (validation, filesystem, logging, formatting)
- [ ] Add comprehensive tests for utilities

### Phase 2: Storage Layer (Week 2)
- [ ] Extract blob storage operations
- [ ] Extract database operations
- [ ] Create S3 abstraction
- [ ] Add storage tests

### Phase 3: Model Layer (Week 3)
- [ ] Extract ensemble model
- [ ] Extract results model
- [ ] Extract properties model
- [ ] Add model tests

### Phase 4: Agent Refactoring (Week 4)
- [ ] Split agent into runner, manager, worker
- [ ] Refactor test execution logic
- [ ] Update process handling
- [ ] Add agent tests

### Phase 5: CLI Refactoring (Week 5)
- [ ] Extract command handlers
- [ ] Improve argument parsing
- [ ] Add output formatters
- [ ] Add CLI tests

### Phase 6: Integration (Week 6)
- [ ] Update imports in existing code
- [ ] Run integration tests
- [ ] Update documentation
- [ ] Performance testing

## Backward Compatibility

During migration, maintain backward compatibility:

```python
# joshua/joshua.py (compatibility shim)
"""Backward compatibility layer."""

# Import from new locations
from joshua.utils.formatting import format_ensemble, format_datetime
from joshua.core.config import get_username

# Maintain old function signatures
def timestamp_of(time_string):
    """Deprecated: Use parse_datetime instead."""
    import warnings
    warnings.warn("timestamp_of is deprecated, use parse_datetime", 
                  DeprecationWarning)
    return parse_datetime(time_string)
```

## Code Review Checklist

When reviewing refactored code:

- [ ] No circular imports
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Unit tests written
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Logging implemented
- [ ] Constants centralized
- [ ] Validation applied
- [ ] Performance maintained

## Common Pitfalls to Avoid

1. **Circular Imports**: Keep dependencies unidirectional
2. **Over-Engineering**: Don't create abstractions for single use cases
3. **Breaking Changes**: Maintain backward compatibility during migration
4. **Missing Tests**: Write tests as you refactor
5. **Poor Naming**: Use clear, descriptive names for modules and functions

## Performance Considerations

The refactored code should maintain or improve performance:

1. **Import Time**: Lazy import heavy dependencies
2. **Memory Usage**: Don't keep unnecessary data in memory
3. **Database Calls**: Batch operations where possible
4. **File I/O**: Use buffered I/O for large files

## Conclusion

This refactoring will transform Joshua from a monolithic codebase into a modular, maintainable system. The key is to migrate gradually, test thoroughly, and maintain backward compatibility during the transition.

Follow this guide section by section, and the codebase will become:
- More maintainable
- Better tested
- Easier to understand
- More robust
- Ready for future enhancements