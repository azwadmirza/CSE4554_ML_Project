    def __init__(self, old_version: str, current_version: str) -> None:
        super().__init__('Build directory has been generated with Meson version {}, '
                         'which is incompatible with the current version {}.'
                         .format(old_version, current_version))
        self.old_version = old_version
        self.current_version = current_version