def _find_worker(relative, follow, done, work, results, errors):
    """Worker thread for collecting stat() results.

    :param str relative: directory to make results relative to
    :param bool follow: if symlinks should be followed
    :param threading.Event done: event indicating that all work has been done
    :param queue.Queue work: queue of paths to process
    :param dict results: shared dictionary for storing all the stat() results
    :param dict errors: shared dictionary for storing any per path errors
    """
    while not done.is_set():
        try:
            entry, parents = work.get(block=False)
        except queue.Empty:
            continue

        if relative:
            path = os.path.relpath(entry, relative)
        else:
            path = entry

        try:
            if follow:
                st = os.stat(entry)
            else:
                st = os.lstat(entry)

            if (st.st_dev, st.st_ino) in parents:
                errors[path] = exceptions.FindError('Sym/hardlink loop found.')
                continue

            parents = parents + [(st.st_dev, st.st_ino)]
            if stat.S_ISDIR(st.st_mode):
                for e in os.listdir(entry):
                    work.put((os.path.join(entry, e), parents))
            elif stat.S_ISREG(st.st_mode):
                results[path] = st
            elif stat.S_ISLNK(st.st_mode):
                errors[path] = exceptions.FindError('Not following symlinks.')
            else:
                errors[path] = exceptions.FindError('Not a file or directory.')

        except OSError as e:
            errors[path] = exceptions.FindError(
                encoding.locale_decode(e.strerror), e.errno)
        finally:
            work.task_done()