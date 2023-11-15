def _get_via_file_cache(cls, py_info_cache, app_data, resolved_path, exe):
    key = sha256(str(resolved_path).encode("utf-8") if PY3 else str(resolved_path)).hexdigest()
    py_info = None
    resolved_path_text = ensure_text(str(resolved_path))
    try:
        resolved_path_modified_timestamp = resolved_path.stat().st_mtime
    except OSError:
        resolved_path_modified_timestamp = -1
    data_file = py_info_cache / "{}.json".format(key)
    with py_info_cache.lock_for_key(key):
        data_file_path = data_file.path
        if data_file_path.exists() and resolved_path_modified_timestamp != 1:  # if exists and matches load
            try:
                data = json.loads(data_file_path.read_text())
                if data["path"] == resolved_path_text and data["st_mtime"] == resolved_path_modified_timestamp:
                    logging.debug("get PythonInfo from %s for %s", data_file_path, exe)
                    py_info = cls._from_dict({k: v for k, v in data["content"].items()})
                else:
                    raise ValueError("force close as stale")
            except (KeyError, ValueError, OSError):
                logging.debug("remove PythonInfo %s for %s", data_file_path, exe)
                data_file_path.unlink()  # close out of date files
        if py_info is None:  # if not loaded run and save
            failure, py_info = _run_subprocess(cls, exe, app_data)
            if failure is None:
                file_cache_content = {
                    "st_mtime": resolved_path_modified_timestamp,
                    "path": resolved_path_text,
                    "content": py_info._to_dict(),
                }
                logging.debug("write PythonInfo to %s for %s", data_file_path, exe)
                data_file_path.write_text(ensure_text(json.dumps(file_cache_content, indent=2)))
            else:
                py_info = failure
    return py_info