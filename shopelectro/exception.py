class Http400(Exception):
    pass


class UpdateCatalogException(BaseException):
    def __init__(self, message=''):
        self.message = message

    def __str__(self, *args, **kwargs):
        return self.message


class DownloadFilesError(UpdateCatalogException):
    def __init__(self, message):
        self.message = message

    def __str__(self, *args, **kwargs):
        return (
            f'Config error. {self.message}.'
        )
