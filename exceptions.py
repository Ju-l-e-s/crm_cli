class CrmError(Exception):
    pass


class CrmForbiddenAccessError(CrmError):
    def __init__(self, *args, **kwargs):
        super().__init__('Forbidden')


class CrmInvalidValue(ValueError):
    pass