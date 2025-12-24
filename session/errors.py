class SessionError(Exception):
    pass

class SessionTimeoutError(SessionError):
    pass

class SessionDisconnectedError(SessionError):
    """Raised when the underlying transport reports a disconnect.

    用於上層分流：
    - 伺服器端：客戶端斷線通常屬正常事件，可降級記錄。
    - 客戶端：若偵測伺服器端斷線，可能需要提示或重連。
    """
    pass