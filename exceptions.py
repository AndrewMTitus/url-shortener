from fastapi import HTTPException

class URLLimitReachedException(HTTPException):
    def __init__(self, detail: str = "You have reached your URL creation limit."):
        super().__init__(status_code=400, detail=detail)

class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = "User not found."):
        super().__init__(status_code=404, detail=detail)

class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid username or password."):
        super().__init__(status_code=401, detail=detail)

class TokenExpiredException(HTTPException):
    def __init__(self, detail: str = "The token has expired."):
        super().__init__(status_code=401, detail=detail)

class URLAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "A URL with the same alias already exists."):
        super().__init__(status_code=409, detail=detail)

class URLNotFoundException(HTTPException):
    def __init__(self, detail: str = "The requested URL was not found."):
        super().__init__(status_code=404, detail=detail)
