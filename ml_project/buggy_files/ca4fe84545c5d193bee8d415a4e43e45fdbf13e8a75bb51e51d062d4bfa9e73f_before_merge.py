    def __init__(self, connection_name: str, connection, lock) -> None:
        self._connection = connection
        self._lock = lock
        self.log = logging.getLogger("db_client")
        self._transaction_class = self.__class__
        self._old_context_value = None
        self.connection_name = connection_name
        self.transaction = None
        self._finalized = False