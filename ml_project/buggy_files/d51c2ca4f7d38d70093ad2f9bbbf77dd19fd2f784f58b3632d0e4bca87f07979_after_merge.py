    def __init__(self, hint=None, **kwargs):
        from .core import project

        if not hint:
            hint = "{0} {1}".format(crayons.red("ERROR (PACKAGE NOT INSTALLED):"), hint)
        filename = project.pipfile_location
        extra = kwargs.pop("extra", [])
        PipenvFileError.__init__(self, filename, decode_for_output(hint), extra=extra, **kwargs)