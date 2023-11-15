    def _get_extract_iter(self) -> Iterator[TableMetadata]:
        for row in self._get_raw_extract_iter():
            columns, i = [], 0

            for column in row["StorageDescriptor"]["Columns"] + row.get(
                "PartitionKeys", []
            ):
                columns.append(
                    ColumnMetadata(
                        column["Name"],
                        column["Comment"] if "Comment" in column else None,
                        column["Type"],
                        i,
                    )
                )
                i += 1

            if self._is_location_parsing_enabled:
                catalog, schema, table = self._parse_location(
                    location=row["StorageDescriptor"]["Location"], name=row["Name"]
                )
            else:
                catalog = None
                schema = None
                table = row["Name"]

            if self._connection_name:
                database = self._connection_name + "/" + row["DatabaseName"]
            else:
                database = row["DatabaseName"]

            yield TableMetadata(
                database,
                catalog,
                schema,
                table,
                row.get("Description") or row.get("Parameters", {}).get("comment"),
                columns,
                row.get("TableType") == "VIRTUAL_VIEW",
            )