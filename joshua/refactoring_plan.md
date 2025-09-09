# Joshua Codebase Refactoring Plan

## Current Issues
1. **Monolithic files**: joshua_agent.py (1097 lines), joshua_model.py (1043 lines), joshua.py (716 lines)
2. **Mixed responsibilities**: Each file handles multiple concerns
3. **Code duplication**: Similar error handling and utility functions scattered
4. **Poor separation of concerns**: Business logic mixed with infrastructure code

## Proposed New Structure

```
joshua/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py           # Central configuration
│   ├── constants.py         # All constants
│   └── exceptions.py        # Custom exceptions
├── models/
│   ├── __init__.py
│   ├── ensemble.py          # Ensemble-related operations
│   ├── results.py           # Results handling
│   └── properties.py        # Property management
├── storage/
│   ├── __init__.py
│   ├── blob.py             # Blob storage operations
│   ├── database.py         # FDB operations
│   └── s3.py               # S3 operations
├── agent/
│   ├── __init__.py
│   ├── runner.py           # Test execution
│   ├── manager.py          # Agent lifecycle
│   └── worker.py           # Worker threads
├── cli/
│   ├── __init__.py
│   ├── commands.py         # CLI commands
│   └── formatters.py       # Output formatting
├── utils/
│   ├── __init__.py
│   ├── validation.py       # Input validation
│   ├── filesystem.py       # File operations
│   ├── process.py          # Process management
│   └── logging.py          # Logging utilities
└── webapp/                 # Keep as is
```

## Refactoring Steps

### Step 1: Extract Core Components
- Move constants to constants.py
- Create central configuration
- Define custom exceptions

### Step 2: Separate Storage Layer
- Extract blob operations
- Isolate database operations
- Create S3 abstraction

### Step 3: Modularize Agent
- Split runner from manager
- Extract worker logic
- Separate ensemble handling

### Step 4: Create Clean CLI
- Separate command handlers
- Extract formatting logic
- Improve argument parsing

### Step 5: Consolidate Utilities
- Centralize validation
- Extract filesystem operations
- Unify logging