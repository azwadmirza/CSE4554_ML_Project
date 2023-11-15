    def set(self, key, value):
        """Insert a doc with value into task attribute and _key as key."""
        try:
            logging.debug(
                'INSERT {{ task: {task}, _key: "{key}" }} INTO {collection}'
                .format(
                    collection=self.collection, key=key, task=value
                )
            )
            self.db.AQLQuery(
                'INSERT {{ task: {task}, _key: "{key}" }} INTO {collection}'
                .format(
                    collection=self.collection, key=key, task=value
                )
            )
        except AQLQueryError as aql_err:
            logging.error(aql_err)
        except Exception as err:
            logging.error(err)