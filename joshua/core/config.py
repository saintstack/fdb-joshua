"""
Central configuration management for Joshua.

This module provides a centralized configuration system that can be
overridden by environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from .constants import *

@dataclass
class JoshuaConfig:
    """Central configuration for Joshua system."""
    
    # FoundationDB Configuration
    fdb_api_version: int = FDB_API_VERSION
    cluster_file: Optional[str] = field(
        default_factory=lambda: os.getenv(ENV_CLUSTER_FILE)
    )
    dir_path: List[str] = field(
        default_factory=lambda: [os.getenv(ENV_JOSHUA_NAMESPACE, "joshua")]
    )
    
    # Agent Configuration
    agent_work_dir: str = field(
        default_factory=lambda: os.getenv("JOSHUA_WORK_DIR", AGENT_DEFAULT_WORK_DIR)
    )
    agent_timeout: Optional[int] = field(
        default_factory=lambda: int(os.getenv("JOSHUA_AGENT_TIMEOUT", "0")) or None
    )
    agent_idle_timeout: Optional[int] = field(
        default_factory=lambda: int(os.getenv("JOSHUA_AGENT_IDLE_TIMEOUT", "0")) or None
    )
    sanity_period: Optional[int] = field(
        default_factory=lambda: int(os.getenv("JOSHUA_SANITY_PERIOD", "0")) or None
    )
    
    # Ensemble Defaults
    default_timeout: int = field(
        default_factory=lambda: int(os.getenv("JOSHUA_DEFAULT_TIMEOUT", str(DEFAULT_TIMEOUT)))
    )
    default_fail_fast: int = field(
        default_factory=lambda: int(os.getenv("JOSHUA_DEFAULT_FAIL_FAST", str(DEFAULT_FAIL_FAST)))
    )
    default_max_runs: int = field(
        default_factory=lambda: int(os.getenv("JOSHUA_DEFAULT_MAX_RUNS", str(DEFAULT_MAX_RUNS)))
    )
    default_priority: int = field(
        default_factory=lambda: int(os.getenv("JOSHUA_DEFAULT_PRIORITY", str(DEFAULT_PRIORITY)))
    )
    
    # Storage Configuration
    blob_key_limit: int = BLOB_KEY_LIMIT
    blob_transaction_limit: int = BLOB_TRANSACTION_LIMIT
    max_tarball_size: int = field(
        default_factory=lambda: int(os.getenv("JOSHUA_MAX_TARBALL_SIZE", str(MAX_TARBALL_SIZE)))
    )
    
    # Artifact Management
    artifact_save_on: str = field(
        default_factory=lambda: os.getenv("JOSHUA_SAVE_ON", ARTIFACT_SAVE_FAILURE)
    )
    artifact_max_age: int = field(
        default_factory=lambda: int(os.getenv("JOSHUA_ARTIFACT_MAX_AGE", str(ARTIFACT_MAX_AGE)))
    )
    
    # Process Management
    process_kill_attempts: int = PROCESS_KILL_ATTEMPTS
    process_wait_timeout: int = PROCESS_WAIT_TIMEOUT
    
    # Logging Configuration
    log_level: str = field(
        default_factory=lambda: os.getenv("JOSHUA_LOG_LEVEL", "INFO")
    )
    log_file: str = field(
        default_factory=lambda: os.getenv("JOSHUA_LOG_FILE", LOG_FILE)
    )
    log_format: str = LOG_FORMAT
    log_max_bytes: int = LOG_MAX_BYTES
    log_backup_count: int = LOG_BACKUP_COUNT
    
    # User Configuration
    username: Optional[str] = field(
        default_factory=lambda: os.getenv(ENV_JOSHUA_USER)
    )
    
    # Debug Options
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("JOSHUA_DEBUG", "").lower() in ("true", "1", "yes")
    )
    dry_run: bool = field(
        default_factory=lambda: os.getenv("JOSHUA_DRY_RUN", "").lower() in ("true", "1", "yes")
    )
    
    def validate(self) -> List[str]:
        """
        Validate configuration settings.
        
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        
        if self.default_timeout <= 0:
            errors.append(f"default_timeout must be positive, got {self.default_timeout}")
        
        if self.default_fail_fast < 0:
            errors.append(f"default_fail_fast must be non-negative, got {self.default_fail_fast}")
        
        if self.default_max_runs < 0:
            errors.append(f"default_max_runs must be non-negative, got {self.default_max_runs}")
        
        if self.default_priority <= 0:
            errors.append(f"default_priority must be positive, got {self.default_priority}")
        
        if self.artifact_save_on not in (ARTIFACT_SAVE_ALWAYS, ARTIFACT_SAVE_FAILURE, ARTIFACT_SAVE_NEVER):
            errors.append(f"artifact_save_on must be one of ALWAYS/FAILURE/NEVER, got {self.artifact_save_on}")
        
        if self.blob_key_limit <= 0:
            errors.append(f"blob_key_limit must be positive, got {self.blob_key_limit}")
        
        if self.blob_transaction_limit <= 0:
            errors.append(f"blob_transaction_limit must be positive, got {self.blob_transaction_limit}")
        
        return errors
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JoshuaConfig':
        """Create configuration from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__dataclass_fields__
        })


# Global configuration instance
config = JoshuaConfig()

def get_config() -> JoshuaConfig:
    """Get the global configuration instance."""
    return config

def set_config(new_config: JoshuaConfig) -> None:
    """Set the global configuration instance."""
    global config
    config = new_config

def reload_config() -> None:
    """Reload configuration from environment variables."""
    global config
    config = JoshuaConfig()