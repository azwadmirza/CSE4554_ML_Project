    def __init__(self, connection):
        self.connection_name = connection.connection_name
        self._connection = connection._connection  # type: aiomysql.Connection
        self._lock = connection._lock
        self.log = logging.getLogger("db_client")
        self._transaction_class = self.__class__
        self._finalized = None  # type: Optional[bool]
        self._old_context_value = None
        self._parent = connection
        self.transaction = None