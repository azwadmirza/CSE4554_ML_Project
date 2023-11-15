def choose_file(multiple: bool) -> List[str]:
    """Select file(s) for uploading, using external command defined in config.

    Args:
        multiple: Should selecting multiple files be allowed.

    Return:
        A list of selected file paths, or empty list if no file is selected.
        If multiple is False, the return value will have at most 1 item.
    """
    handle = tempfile.NamedTemporaryFile(prefix='qutebrowser-fileselect-', delete=False)
    handle.close()
    tmpfilename = handle.name
    with utils.cleanup_file(tmpfilename):
        if multiple:
            command = config.val.fileselect.multiple_files.command
        else:
            command = config.val.fileselect.single_file.command

        proc = guiprocess.GUIProcess(what='choose-file')
        proc.start(command[0],
                   [arg.replace('{}', tmpfilename) for arg in command[1:]])

        loop = qtutils.EventLoop()
        proc.finished.connect(lambda _code, _status: loop.exit())
        loop.exec()

        try:
            with open(tmpfilename, mode='r', encoding=sys.getfilesystemencoding()) as f:
                selected_files = f.read().splitlines()
        except OSError as e:
            message.error(f"Failed to open tempfile {tmpfilename} ({e})!")
            selected_files = []

    if not multiple:
        if len(selected_files) > 1:
            message.warning("More than one file chosen, using only the first")
            return selected_files[:1]
    return selected_files