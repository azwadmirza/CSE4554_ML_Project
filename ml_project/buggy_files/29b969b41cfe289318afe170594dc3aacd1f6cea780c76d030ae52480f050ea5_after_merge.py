    def post_create_table(self, table):
        """Build table-level CREATE options like ENGINE and COLLATE."""

        table_opts = []

        opts = dict(
            (k[len(self.dialect.name) + 1 :].upper(), v)
            for k, v in table.kwargs.items()
            if k.startswith("%s_" % self.dialect.name)
        )

        if table.comment is not None:
            opts["COMMENT"] = table.comment

        partition_options = [
            "PARTITION_BY",
            "PARTITIONS",
            "SUBPARTITIONS",
            "SUBPARTITION_BY",
        ]

        nonpart_options = set(opts).difference(partition_options)
        part_options = set(opts).intersection(partition_options)

        for opt in topological.sort(
            [
                ("DEFAULT_CHARSET", "COLLATE"),
                ("DEFAULT_CHARACTER_SET", "COLLATE"),
                ("CHARSET", "COLLATE"),
                ("CHARACTER_SET", "COLLATE"),
            ],
            nonpart_options,
        ):
            arg = opts[opt]
            if opt in _reflection._options_of_type_string:

                arg = self.sql_compiler.render_literal_value(
                    arg, sqltypes.String()
                )

            if opt in (
                "DATA_DIRECTORY",
                "INDEX_DIRECTORY",
                "DEFAULT_CHARACTER_SET",
                "CHARACTER_SET",
                "DEFAULT_CHARSET",
                "DEFAULT_COLLATE",
            ):
                opt = opt.replace("_", " ")

            joiner = "="
            if opt in (
                "TABLESPACE",
                "DEFAULT CHARACTER SET",
                "CHARACTER SET",
                "COLLATE",
            ):
                joiner = " "

            table_opts.append(joiner.join((opt, arg)))

        for opt in topological.sort(
            [
                ("PARTITION_BY", "PARTITIONS"),
                ("PARTITION_BY", "SUBPARTITION_BY"),
                ("PARTITION_BY", "SUBPARTITIONS"),
                ("PARTITIONS", "SUBPARTITIONS"),
                ("PARTITIONS", "SUBPARTITION_BY"),
                ("SUBPARTITION_BY", "SUBPARTITIONS"),
            ],
            part_options,
        ):
            arg = opts[opt]
            if opt in _reflection._options_of_type_string:
                arg = self.sql_compiler.render_literal_value(
                    arg, sqltypes.String()
                )

            opt = opt.replace("_", " ")
            joiner = " "

            table_opts.append(joiner.join((opt, arg)))

        return " ".join(table_opts)