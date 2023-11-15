    def insert_statement(self):
        names = list(map(str, self.frame.columns))
        wld = "?"  # wildcard char
        escape = _get_valid_sqlite_name

        if self.index is not None:
            for idx in self.index[::-1]:
                names.insert(0, idx)

        bracketed_names = [escape(column) for column in names]
        col_names = ",".join(bracketed_names)
        wildcards = ",".join([wld] * len(names))
        insert_statement = (
            f"INSERT INTO {escape(self.name)} ({col_names}) VALUES ({wildcards})"
        )
        return insert_statement