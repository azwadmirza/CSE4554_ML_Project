    def table(self, name: str, path: Optional[str] = None) -> ir.TableExpr:
        if name not in self.list_tables(path):
            raise AttributeError(name)

        if path is None:
            path = self.root

        # get the schema
        f = path / "{}.parquet".format(name)

        parquet_file = pq.ParquetFile(str(f))
        schema = sch.infer(parquet_file.schema)

        table = self.table_class(name, schema, self).to_expr()
        self.dictionary[name] = f

        return table