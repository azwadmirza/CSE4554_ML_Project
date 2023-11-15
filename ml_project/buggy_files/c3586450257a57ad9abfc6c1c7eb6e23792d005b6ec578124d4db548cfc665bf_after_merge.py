def _load_json_file(file: str, manager: BuildManager,
                    log_sucess: str, log_error: str) -> Optional[Dict[str, Any]]:
    """A simple helper to read a JSON file with logging."""
    try:
        data = manager.metastore.read(file)
    except IOError:
        manager.log(log_error + file)
        return None
    manager.trace(log_sucess + data.rstrip())
    try:
        result = json.loads(data)
    except ValueError:  # TODO: JSONDecodeError in 3.5
        manager.errors.set_file(file, None)
        manager.errors.report(-1, -1,
                              "Error reading JSON file;"
                              " you likely have a bad cache.\n"
                              "Try removing the {cache_dir} directory"
                              " and run mypy again.".format(
                                  cache_dir=manager.options.cache_dir
                              ),
                              blocker=True)
        return None
    else:
        return result