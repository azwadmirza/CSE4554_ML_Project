    def __init__(self) -> None:
        try:
            self._coinmarketcap = Pymarketcap()
        except BaseException:
            self._coinmarketcap = None

        self._pairs = []