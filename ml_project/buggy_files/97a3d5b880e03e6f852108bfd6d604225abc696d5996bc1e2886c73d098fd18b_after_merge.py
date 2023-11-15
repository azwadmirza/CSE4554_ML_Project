def atomic_directory(target_dir, exclusive, source=None):
    # type: (str, bool, Optional[str]) -> Iterator[Optional[str]]
    """A context manager that yields a new empty work directory path it will move to `target_dir`.

    :param target_dir: The target directory to atomically update.
    :param exclusive: If `True`, its guaranteed that only one process will be yielded a non `None`
                      workdir; otherwise two or more processes might be yielded unique non-`None`
                      workdirs with the last process to finish "winning".
    :param source: An optional source offset into the work directory to use for the atomic update
                   of the target directory. By default the whole work directory is used.

    If the `target_dir` already exists the enclosed block will be yielded `None` to signal there is
    no work to do.

    If the enclosed block fails the `target_dir` will be undisturbed.

    The new work directory will be cleaned up regardless of whether or not the enclosed block
    succeeds.

    If the contents of the resulting directory will be subsequently mutated it's probably correct to
    pass `exclusive=True` to ensure mutations that race the creation process are not lost.
    """
    atomic_dir = AtomicDirectory(target_dir=target_dir)
    if atomic_dir.is_finalized:
        # Our work is already done for us so exit early.
        yield None
        return

    lock_fd = None  # type: Optional[int]
    if exclusive:
        head, tail = os.path.split(atomic_dir.target_dir)
        if head:
            safe_mkdir(head)
        # N.B.: We don't actually write anything to the lock file but the fcntl file locking
        # operations only work on files opened for at least write.
        lock_fd = os.open(
            os.path.join(head, ".{}.atomic_directory.lck".format(tail or "here")),
            os.O_CREAT | os.O_WRONLY,
        )
        # N.B.: Since lockf operates on an open file descriptor and these are guaranteed to be
        # closed by the operating system when the owning process exits, this lock is immune to
        # staleness.
        fcntl.lockf(lock_fd, fcntl.LOCK_EX)  # A blocking write lock.
        if atomic_dir.is_finalized:
            # We lost the double-checked locking race and our work was done for us by the race
            # winner so exit early.
            yield None
            return

    safe_mkdir(atomic_dir.work_dir)
    try:
        yield atomic_dir.work_dir
        atomic_dir.finalize(source=source)
    finally:
        if lock_fd is not None:
            fcntl.lockf(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
        atomic_dir.cleanup()