    def __init__(self, filename="Pipfile.lock", extra=None, **kwargs):
        extra = kwargs.pop("extra", [])
        message = "{0} {1} {2}".format(
            crayons.white("You need to run", bold=True),
            crayons.red("$ pipenv lock", bold=True),
            crayons.white("before you can continue.", bold=True)
        )
        super(LockfileNotFound, self).__init__(filename, message=fix_utf8(message), extra=extra, **kwargs)