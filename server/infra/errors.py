class RoomManagerError(Exception):
    """Base class for RoomManager related errors."""
    pass

class PlayerAlreadyInRoomError(RoomManagerError):
    """Raised when a player is already in a room."""
    pass

class RoomIDGenerationError(RoomManagerError):
    """Raised when unable to generate a unique room ID."""
    pass