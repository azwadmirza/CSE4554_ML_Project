    def __init__(self, db):
        self._batch = db._db.write_batch()