def get_monkey_dir_path():
    if is_windows_os():
        return WormConfiguration.monkey_dir_windows
    else:
        return WormConfiguration.monkey_dir_linux