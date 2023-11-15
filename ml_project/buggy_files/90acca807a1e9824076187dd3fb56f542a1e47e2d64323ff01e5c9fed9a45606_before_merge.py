    def __init__(self, connection_name, connection, lock):
        self.connection_name = connection_name
        self._connection = connection
        self._lock = lock
        self.log = logging.getLogger("db_client")
        self._transaction_class = self.__class__
        self._finalized = False
        self._old_context_value = None