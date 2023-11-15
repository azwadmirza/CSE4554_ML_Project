def init_long_path(target_path):
    win_ver, _, win_rev = context.os_distribution_name_version[1].split('.')
    # win10, build 14352 was the first preview release that supported this
    if int(win_ver) >= 10 and int(win_rev) >= 14352:
        prev_value, value_type = _read_windows_registry(target_path)
        if str(prev_value) != "1":
            if context.verbosity:
                print('\n')
                print(target_path)
                print(make_diff(str(prev_value), '1'))
            if not context.dry_run:
                _write_windows_registry(target_path, 1, winreg.REG_DWORD)
            return Result.MODIFIED
        else:
            return Result.NO_CHANGE
    else:
        if context.verbosity:
            print('\n')
            print('Not setting long path registry key; Windows version must be at least 10 with '
                  'the fall 2016 "Anniversary update" or newer.')
            return Result.NO_CHANGE