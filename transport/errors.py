class FramedSocketError(Exception):
    """Base class for connector-related errors.

    Stores optional structured context to make debugging easier:
    - cause: original exception instance (if any)
    - peer: remote address string (if applicable)
    - errno: optional error number
    """
    def __init__(self, message: str | None = None, *, cause: Exception | None = None, peer: str | None = None, errno: int | None = None):
        super().__init__(message)
        # Keep optional context for programmatic use, but keep str() simple.
        self.cause = cause
        self.peer = peer
        self.errno = errno

    def __str__(self) -> str:
        # Simple, concise representation per request: "ClassName: message" or just "ClassName".
        msg = super().__str__()
        if msg:
            return f"{self.__class__.__name__}: {msg}"
        return self.__class__.__name__

class DisconnectedError(FramedSocketError):
    """Raised when a connector is disconnected unexpectedly."""
    pass

class InteractionTimeoutError(FramedSocketError):
    """Raised when interaction (e.g., send/receive) attempt times out."""
    pass

class InvalidConfigurationError(FramedSocketError):
    """Raised when the connector configuration is invalid."""
    pass

class AuthenticationError(FramedSocketError):
    """Raised when authentication with the connector fails."""
    pass

class DataTransmissionError(FramedSocketError):
    """Raised when there is an error during data transmission."""
    pass