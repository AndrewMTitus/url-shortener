class URLShortenerException(Exception):
    def __init__(self, message: str):
        self.message = message

class URLAlreadyExistsException(URLShortenerException):
    pass

class URLNotFoundException(URLShortenerException):
    pass

class URLLimitReachedException(Exception):
    def __init__(self, message="URL limit has been reached"):
        self.message = message
        super().__init__(self.message)
