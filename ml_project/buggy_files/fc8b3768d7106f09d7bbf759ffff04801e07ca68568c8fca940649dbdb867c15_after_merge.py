def rename(source_path, destination_path, force=False):
    if lexists(destination_path) and force:
        rm_rf(destination_path)
    if lexists(source_path):
        log.trace("renaming %s => %s", source_path, destination_path)
        try:
            os_rename(source_path, destination_path)
        except EnvironmentError as e:
            if e.errno in (EINVAL, EXDEV):
                # https://github.com/conda/conda/issues/6811
                # https://github.com/conda/conda/issues/6711
                log.trace("Could not rename %s => %s due to errno [%s]. Falling back"
                          " to copy/unlink", source_path, destination_path, e.errno)
                # https://github.com/moby/moby/issues/25409#issuecomment-238537855
                # shutil.move() falls back to copy+unlink
                move(source_path, destination_path)
            else:
                raise
    else:
        log.trace("cannot rename; source path does not exist '%s'", source_path)