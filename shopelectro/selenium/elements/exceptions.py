class Unavailable(NotImplementedError):

    def __init__(self, msg, *args, **kwargs):
        super().__init__(f'The element doesn\'t provide ability to {msg}', *args, **kwargs)
