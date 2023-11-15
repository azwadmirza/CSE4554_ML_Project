def run_with_input(context, command, inputs=""):
    # create an iterator through all inputs. These inputs will be fed one by one
    # to the mocked calls for 'input()', 'util.getpass()' and 'sys.stdin.read()'
    if context.text:
        text = iter(context.text.split("\n"))
    else:
        text = iter([inputs])

    args = ushlex(command)[1:]

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
        password = text

    # fmt: off
    # see: https://github.com/psf/black/issues/664
    with \
        patch("builtins.input", side_effect=_mock_input(text)) as mock_input, \
        patch("getpass.getpass", side_effect=_mock_getpass(password)) as mock_getpass, \
        patch("sys.stdin.read", side_effect=text) as mock_read, \
        patch("subprocess.call", side_effect=_mock_editor) as mock_editor, \
        patch("jrnl.config.get_config_path", side_effect=lambda: context.config_path), \
        patch("jrnl.install.get_config_path", side_effect=lambda: context.config_path) \
    :
        try:
            cli(args or [])
            context.exit_status = 0
        except SystemExit as e:
            context.exit_status = e.code

        # put mocks into context so they can be checked later in "then" statements
        context.editor = mock_editor
        context.input = mock_input
        context.getpass = mock_getpass
        context.read = mock_read
        context.iter_text = text

        context.execute_steps('''
            Then all input was used
            And at least one input method was called
        ''')