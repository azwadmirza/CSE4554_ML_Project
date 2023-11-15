def _config_from_pyproject(path):
    if os.path.isfile(path):
        try:
            with open(path, "r") as f:
                pyproject = tomlkit.loads(f.read())
            if pyproject:
                return pyproject.get("tool", {}).get("semantic_release", {})
        except TOMLKitError as e:
            logger.debug(f"Could not decode pyproject.toml: {e}")

    return {}