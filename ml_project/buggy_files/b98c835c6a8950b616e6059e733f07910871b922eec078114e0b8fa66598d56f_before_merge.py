    def __init__(self, osutils=None):
        # type: (Optional[OSUtils]) -> None
        if osutils is None:
            osutils = OSUtils()
        self._osutils = osutils