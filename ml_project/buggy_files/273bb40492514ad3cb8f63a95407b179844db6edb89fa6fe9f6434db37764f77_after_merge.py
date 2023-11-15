    def fill_from_lock(stage, lock_data=None):
        """Fill values for params, checksums for outs and deps from lock."""
        if not lock_data:
            return

        assert isinstance(lock_data, dict)
        items = chain(
            ((StageParams.PARAM_DEPS, dep) for dep in stage.deps),
            ((StageParams.PARAM_OUTS, out) for out in stage.outs),
        )

        checksums = {
            key: {item["path"]: item for item in lock_data.get(key, {})}
            for key in [StageParams.PARAM_DEPS, StageParams.PARAM_OUTS]
        }
        for key, item in items:
            path = item.def_path
            if isinstance(item, dependency.ParamsDependency):
                item.fill_values(get_in(lock_data, [stage.PARAM_PARAMS, path]))
                continue
            info = get_in(checksums, [key, path], {})
            info = info.copy()
            info.pop("path", None)
            item.hash_info = HashInfo.from_dict(info)