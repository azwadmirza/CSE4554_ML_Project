    def _unsafe_process(self, fname, in_str=None, config=None):
        if not config:
            raise ValueError(
                "For the dbt templater, the `process()` method requires a config object."
            )
        if not fname:
            raise ValueError(
                "For the dbt templater, the `process()` method requires a file name"
            )
        elif fname == "stdin":
            raise ValueError(
                "The dbt templater does not support stdin input, provide a path instead"
            )
        self.sqlfluff_config = config

        selected = self.dbt_selector_method.search(
            included_nodes=self.dbt_manifest.nodes,
            # Selector needs to be a relative path
            selector=os.path.relpath(fname, start=os.getcwd()),
        )
        results = [self.dbt_manifest.expect(uid) for uid in selected]

        if not results:
            raise RuntimeError("File %s was not found in dbt project" % fname)

        node = self.dbt_compiler.compile_node(
            node=results[0],
            manifest=self.dbt_manifest,
        )

        if hasattr(node, "injected_sql"):
            # If injected SQL is present, it contains a better picture
            # of what will actually hit the database (e.g. with tests).
            # However it's not always present.
            compiled_sql = node.injected_sql
        else:
            compiled_sql = node.compiled_sql

        if not compiled_sql:
            raise SQLTemplaterError(
                "dbt templater compilation failed silently, check your configuration "
                "by running `dbt compile` directly."
            )

        raw_sliced, sliced_file, templated_sql = self.slice_file(
            node.raw_sql, compiled_sql, config=config
        )
        return (
            TemplatedFile(
                source_str=node.raw_sql,
                templated_str=templated_sql,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            # No violations returned in this way.
            [],
        )