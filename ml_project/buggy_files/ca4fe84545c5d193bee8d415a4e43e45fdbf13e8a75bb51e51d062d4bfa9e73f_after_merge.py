    def __init__(self, connection) -> None:
        self._connection = connection._connection
        self._lock = connection._lock
        self.log = logging.getLogger("db_client")
        self._transaction_class = self.__class__
        self._old_context_value = None
        self.connection_name = connection.connection_name
        self.transaction = None
        self._finalized = False
        self._parent = connection