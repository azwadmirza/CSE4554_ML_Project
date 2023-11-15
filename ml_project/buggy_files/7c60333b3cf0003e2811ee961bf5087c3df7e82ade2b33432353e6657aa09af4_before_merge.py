    def load(cls, task=None):
        """Load all key/values from `task` into memory from database."""
        with Session() as session:
            for skv in session.query(SimpleKeyValue).filter(SimpleKeyValue.task == task).all():
                cls.class_store[task][skv.plugin][skv.key] = skv.value