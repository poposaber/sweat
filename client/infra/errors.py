class ConnectorError(Exception):
    """Base class for connector-related errors."""
    pass

class ConnectionTimeoutError(ConnectorError):
    """Raised when a connection attempt times out."""
    pass