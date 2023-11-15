def _build_load_agate_table(
    model: Union[ParsedSeedNode, CompiledSeedNode]
) -> Callable[[], agate.Table]:
    def load_agate_table():
        path = model.seed_file_path
        try:
            table = dbt.clients.agate_helper.from_csv(path)
        except ValueError as e:
            dbt.exceptions.raise_compiler_error(str(e))
        table.original_abspath = os.path.abspath(path)
        return table
    return load_agate_table