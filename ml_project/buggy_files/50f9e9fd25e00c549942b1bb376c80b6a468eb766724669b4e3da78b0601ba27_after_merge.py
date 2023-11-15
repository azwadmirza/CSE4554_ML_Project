    def __init__(self, database: Database, db_conn, hs):
        super(MonthlyActiveUsersStore, self).__init__(database, db_conn, hs)

        # Do not add more reserved users than the total allowable number
        # cur = LoggingTransaction(
        self.db.new_transaction(
            db_conn,
            "initialise_mau_threepids",
            [],
            [],
            self._initialise_reserved_users,
            hs.config.mau_limits_reserved_threepids[: self.hs.config.max_mau_value],
        )