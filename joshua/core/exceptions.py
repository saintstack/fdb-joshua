"""
Custom exceptions for the Joshua system.

This module centralizes all custom exceptions used throughout the Joshua codebase,
providing clear error types for different failure scenarios.
"""

class JoshuaError(Exception):
    """Base exception for all Joshua-specific errors."""
    
    def __init__(self, message: str, code: int = None):
        """
        Initialize JoshuaError.
        
        Args:
            message: Error message
            code: Optional error code for categorization
        """
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.code:
            return f"JoshuaError({self.code}): {self.message}"
        return f"JoshuaError: {self.message}"


class JoshuaTimeout(JoshuaError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str, timeout_seconds: int = None):
        """
        Initialize JoshuaTimeout.
        
        Args:
            message: Error message
            timeout_seconds: Number of seconds before timeout occurred
        """
        super().__init__(message, code=1001)
        self.timeout_seconds = timeout_seconds


class JoshuaValidationError(JoshuaError):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, value: any, reason: str):
        """
        Initialize JoshuaValidationError.
        
        Args:
            field: Field that failed validation
            value: The invalid value
            reason: Reason for validation failure
        """
        message = f"Validation failed for {field}='{value}': {reason}"
        super().__init__(message, code=1002)
        self.field = field
        self.value = value
        self.reason = reason


class JoshuaDatabaseError(JoshuaError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: str = None):
        """
        Initialize JoshuaDatabaseError.
        
        Args:
            message: Error message
            operation: The database operation that failed
        """
        super().__init__(message, code=2001)
        self.operation = operation


class JoshuaAgentError(JoshuaError):
    """Raised when agent operations fail."""
    
    def __init__(self, message: str, agent_id: str = None):
        """
        Initialize JoshuaAgentError.
        
        Args:
            message: Error message
            agent_id: ID of the agent that failed
        """
        super().__init__(message, code=3001)
        self.agent_id = agent_id


class JoshuaEnsembleError(JoshuaError):
    """Raised when ensemble operations fail."""
    
    def __init__(self, message: str, ensemble_id: str = None):
        """
        Initialize JoshuaEnsembleError.
        
        Args:
            message: Error message
            ensemble_id: ID of the ensemble that failed
        """
        super().__init__(message, code=4001)
        self.ensemble_id = ensemble_id


class JoshuaStorageError(JoshuaError):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, path: str = None):
        """
        Initialize JoshuaStorageError.
        
        Args:
            message: Error message
            path: Path that caused the error
        """
        super().__init__(message, code=5001)
        self.path = path