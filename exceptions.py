class URLShortenerException(Exception):
    def __init__(self, message: str):
        self.message = message

class URLAlreadyExistsException(URLShortenerException):
    pass

class URLNotFoundException(URLShortenerException):
    pass

