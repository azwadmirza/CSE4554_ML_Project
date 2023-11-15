    def expect_compound_columns_to_be_unique(
        self,
        column_list,
        ignore_row_if="all_values_are_missing",
        result_format=None,
        row_condition=None,
        condition_parser=None,
        include_config=True,
        catch_exceptions=None,
        meta=None,
    ):
        columns = [
            sa.column(col["name"]) for col in self.columns if col["name"] in column_list
        ]
        query = (
            sa.select([sa.func.count()])
            .group_by(*columns)
            .having(sa.func.count() > 1)
            .select_from(self._table)
        )

        if ignore_row_if == "all_values_are_missing":
            query = query.where(sa.and_(*[col != None for col in columns]))
        elif ignore_row_if == "any_value_is_missing":
            query = query.where(sa.or_(*[col != None for col in columns]))
        elif ignore_row_if == "never":
            pass
        else:
            raise ValueError(
                "ignore_row_if was set to an unexpected value: %s" % ignore_row_if
            )

        unexpected_count = self.engine.execute(query).fetchone()

        if unexpected_count is None:
            # This can happen when the condition filters out all rows
            unexpected_count = 0
        else:
            unexpected_count = unexpected_count[0]

        total_count_query = sa.select([sa.func.count()]).select_from(self._table)
        total_count = self.engine.execute(total_count_query).fetchone()[0]

        if total_count > 0:
            unexpected_percent = 100.0 * unexpected_count / total_count
        else:
            # If no rows, then zero percent are unexpected.
            unexpected_percent = 0

        return {
            "success": unexpected_count == 0,
            "result": {"unexpected_percent": unexpected_percent},
        }