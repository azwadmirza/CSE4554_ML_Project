def _load_json_file(file: str, manager: BuildManager,
                    log_sucess: str, log_error: str) -> Optional[Dict[str, Any]]:
    """A simple helper to read a JSON file with logging."""
    try:
        data = manager.metastore.read(file)
    except IOError:
        manager.log(log_error + file)
        return None
    manager.trace(log_sucess + data.rstrip())
    result = json.loads(data)  # TODO: Errors
    return result