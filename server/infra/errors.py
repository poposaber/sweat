class RoomManagerError(Exception):
    """Base class for RoomManager related errors."""
    pass

class PlayerAlreadyInRoomError(RoomManagerError):
    """Raised when a player is already in a room."""
    pass

class PlayerNotInRoomError(RoomManagerError):
    """Raised when a player is not in the specified room."""
    pass

class RoomIDGenerationError(RoomManagerError):
    """Raised when unable to generate a unique room ID."""
    pass

class RoomFullError(RoomManagerError):
    """Raised when trying to add a player to a full room."""
    pass

class RoomNotFoundError(RoomManagerError):
    """Raised when a room is not found."""
    pass