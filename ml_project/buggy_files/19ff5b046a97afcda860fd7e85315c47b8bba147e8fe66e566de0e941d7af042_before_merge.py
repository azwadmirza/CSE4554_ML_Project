def run(context, command, text=""):
    text = text or context.text or ""

    if "cache_dir" in context and context.cache_dir is not None:
        cache_dir = os.path.join("features", "cache", context.cache_dir)
        command = command.format(cache_dir=cache_dir)

    args = ushlex(command)

    def _mock_editor(command):
        context.editor_command = command
        tmpfile = command[-1]
        with open(tmpfile, "r") as editor_file:
            file_content = editor_file.read()
        context.editor_file = {"name": tmpfile, "content": file_content}
        Path(tmpfile).touch()

    if "password" in context:
        password = context.password
    else:
        password = iter(text)

    try:
        # fmt: off
        # see: https://github.com/psf/black/issues/664
        with \
            patch("sys.argv", args), \
            patch("getpass.getpass", side_effect=_mock_getpass(password)) as mock_getpass, \
            patch("subprocess.call", side_effect=_mock_editor) as mock_editor, \
            patch("sys.stdin.read", side_effect=lambda: text) \
        :
            context.editor = mock_editor
            context.getpass = mock_getpass
            cli(args[1:])
            context.exit_status = 0
        # fmt: on
    except SystemExit as e:
        context.exit_status = e.code