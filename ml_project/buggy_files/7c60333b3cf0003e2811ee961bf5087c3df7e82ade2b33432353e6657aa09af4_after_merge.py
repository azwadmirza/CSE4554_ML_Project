    def load(cls, task=None):
        """Load all key/values from `task` into memory from database."""
        with Session() as session:
            for skv in session.query(SimpleKeyValue).filter(SimpleKeyValue.task == task).all():
                try:
                    cls.class_store[task][skv.plugin][skv.key] = skv.value
                except TypeError as e:
                    log.warning('Value stored in simple_persistence cannot be decoded. It will be removed. Error: %s',
                                str(e))
                    cls.class_store[task][skv.plugin][skv.key] = DELETE