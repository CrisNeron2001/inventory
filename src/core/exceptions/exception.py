class TemporaryFailure(Exception):
    def __init__(self, msg: str = "Temporary error"):
        self.msg = msg
        super().__init__(self.msg)

class PermanentFailure(Exception):
    def __init__(self, msg: str = "Permanent error"):
        self.msg = msg
        super().__init__(self.msg)

class DatabaseFailure(Exception):
    def __init__(self, msg: str = "Database error"):
        self.msg = msg
        super().__init__(self.msg)
        

class ConnectionFailure(Exception):
    def __init__(self, msg: str = "Connection error"):
        self.msg = msg
        super().__init__(self.msg)


class AuthorizationFailure(Exception):
    def __init__(self, msg: str = "Not authorized to perform this action"):
        self.msg = msg
        super().__init__(self.msg)