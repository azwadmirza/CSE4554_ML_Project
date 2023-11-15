def clear_screen() -> None:     # pragma: no cover
    command = 'clear'
    if platform.system() == 'Windows':
        command = 'cls'
    os.system(command)