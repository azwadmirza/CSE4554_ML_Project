    def __init__(self, osutils=None, import_string=None):
        # type: (Optional[OSUtils], OptStr) -> None
        if osutils is None:
            osutils = OSUtils()
        self._osutils = osutils
        if import_string is None:
            import_string = pip_import_string()
        self._import_string = import_string