    def __init__(self, window=None):
        # type: (sublime.Window) -> None
        self._window = window or sublime.active_window()
        self._global_settings = get_global_settings()