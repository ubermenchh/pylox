

class Return_(RuntimeError):
    def __init__(self, value, message=None):
        super().__init__(message)
        self.value = value
