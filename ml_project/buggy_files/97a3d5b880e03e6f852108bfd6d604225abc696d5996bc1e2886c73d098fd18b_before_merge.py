def atomic_directory(target_dir, source=None):
    """A context manager that yields a new empty work directory path it will move to `target_dir`.

    :param str target_dir: The target directory to atomically update.
    :param str source: An optional source offset into the work directory to use for the atomic update
                       of the target directory. By default the whole work directory is used.

    If the `target_dir` already exists the enclosed block will be yielded `None` to signal there is
    no work to do.

    If the enclosed block fails the `target_dir` will be undisturbed.

    The new work directory will be cleaned up regardless of whether or not the enclosed block
    succeeds.
    """
    atomic_dir = AtomicDirectory(target_dir=target_dir)
    if atomic_dir.is_finalized:
        yield None
        return

    safe_mkdir(atomic_dir.work_dir)
    try:
        yield atomic_dir.work_dir
        atomic_dir.finalize(source=source)
    finally:
        atomic_dir.cleanup()