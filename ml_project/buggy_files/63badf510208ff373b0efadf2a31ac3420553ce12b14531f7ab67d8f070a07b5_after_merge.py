def get_path_output(
        rel: pgast.BaseRelation, path_id: irast.PathId, *,
        aspect: str, allow_nullable: bool=True,
        ptr_info: Optional[pg_types.PointerStorageInfo]=None,
        env: context.Environment) -> pgast.OutputVar:

    if isinstance(rel, pgast.Query):
        path_id = map_path_id(path_id, rel.view_path_id_map)

    return _get_path_output(rel, path_id=path_id, aspect=aspect,
                            ptr_info=ptr_info, allow_nullable=allow_nullable,
                            env=env)