def open_editor_and_enter(context, method, text=""):
    text = text or context.text or ""

    if method == "enter":
        file_method = "w+"
    elif method == "append":
        file_method = "a"
    else:
        file_method = "r+"

    def _mock_editor(command):
        context.editor_command = command
        tmpfile = command[-1]
        with open(tmpfile, file_method) as f:
            f.write(text)

        return tmpfile

    if "password" in context:
        password = context.password
    else:
        password = ""

    # fmt: off
    # see: https://github.com/psf/black/issues/664
    with \
        patch("subprocess.call", side_effect=_mock_editor) as mock_editor, \
        patch("getpass.getpass", side_effect=_mock_getpass(password)) as mock_getpass, \
        patch("sys.stdin.isatty", return_value=True) \
    :
        context.editor = mock_editor
        context.getpass = mock_getpass
        cli(["--edit"])