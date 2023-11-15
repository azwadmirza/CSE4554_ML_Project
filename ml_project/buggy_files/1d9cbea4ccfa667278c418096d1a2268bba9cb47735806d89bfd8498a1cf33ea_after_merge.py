    def _create_record_and_aggregate_column(
        trial: "optuna.trial.FrozenTrial",
    ) -> Dict[Tuple[str, str], Any]:

        record = {}
        for attr, df_column in attrs_to_df_columns.items():
            value = getattr(trial, attr)
            if isinstance(value, TrialState):
                # Convert TrialState to str and remove the common prefix.
                value = str(value).split(".")[-1]
            if isinstance(value, dict):
                for nested_attr, nested_value in value.items():
                    record[(df_column, nested_attr)] = nested_value
                    column_agg[attr].add((df_column, nested_attr))
            elif isinstance(value, list):
                # Expand trial.values.
                for nested_attr, nested_value in enumerate(value):
                    record[(df_column, nested_attr)] = nested_value
                    column_agg[attr].add((df_column, nested_attr))
            elif attr == "values":
                # trial.values should be None when the trial's state is FAIL or PRUNED.
                assert value is None
                for nested_attr in range(len(study.directions)):
                    record[(df_column, nested_attr)] = None
                    column_agg[attr].add((df_column, nested_attr))
            else:
                record[(df_column, non_nested_attr)] = value
                column_agg[attr].add((df_column, non_nested_attr))
        return record