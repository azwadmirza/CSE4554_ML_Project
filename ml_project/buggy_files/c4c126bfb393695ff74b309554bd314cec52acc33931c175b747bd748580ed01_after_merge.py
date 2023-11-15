    def __init__(self, db):
        # Using transaction and sync in Windows to prevent CorruptionError
        self._batch = db._db.write_batch(transaction=True, sync=True)