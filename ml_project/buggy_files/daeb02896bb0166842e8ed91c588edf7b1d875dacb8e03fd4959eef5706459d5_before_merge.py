def _worker_check_single_file(file_item):
    name, filepath, modname = file_item

    _worker_linter.open()
    _worker_linter.check_single_file(name, filepath, modname)

    msgs = [_get_new_args(m) for m in _worker_linter.reporter.messages]
    return (
        _worker_linter.current_name,
        _worker_linter.file_state.base_name,
        msgs,
        _worker_linter.stats,
        _worker_linter.msg_status,
    )