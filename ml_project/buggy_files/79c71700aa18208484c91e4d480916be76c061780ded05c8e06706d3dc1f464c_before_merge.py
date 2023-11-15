        def applyier(df, other):
            concated = pandas.concat([df, other], axis=1, copy=False)
            result = concated.pivot_table(
                index=index,
                values=values if len(values) > 0 else None,
                columns=columns,
                aggfunc=aggfunc,
                fill_value=fill_value,
                margins=margins,
                dropna=dropna,
                margins_name=margins_name,
                observed=observed,
            )

            # in that case Pandas transposes the result of `pivot_table`,
            # transposing it back to be consistent with column axis values along
            # different partitions
            if len(index) == 0 and len(columns) > 0:
                result = result.T

            return result