    def __init__(self, app):
        # type: (Any) -> None
        self.app = app

        if _looks_like_asgi3(app):
            self.__call__ = self._run_asgi3  # type: Callable[..., Any]
        else:
            self.__call__ = self._run_asgi2