def normexe(orig_exe):
    if os.sep not in orig_exe:
        exe = find_executable(orig_exe)
        if exe is None:
            raise ExecutableNotFoundError(
                'Executable `{}` not found'.format(orig_exe),
            )
        return exe
    else:
        return orig_exe