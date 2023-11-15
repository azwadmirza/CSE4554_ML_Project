    def init_on_load(self):
        """
        Called by the ORM after the instance has been loaded from the DB or otherwise reconstituted
        i.e automatically deserialize Xcom value when loading from DB.
        """
        try:
            self.value = self.orm_deserialize_value()
        except (UnicodeEncodeError, ValueError):
            # For backward-compatibility.
            # Preventing errors in webserver
            # due to XComs mixed with pickled and unpickled.
            self.value = pickle.loads(self.value)