class ConnectorError(Exception):
    """Base class for connector-related errors."""
    pass

class ConnectionTimeoutError(ConnectorError):
    """Raised when a connection attempt times out."""
    pass

class DuplicatorError(Exception):
    """Base class for duplicator-related errors."""
    pass

class SourceNotFoundError(DuplicatorError):
    """Raised when the source path for duplication is not found."""
    pass

