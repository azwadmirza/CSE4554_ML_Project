def extract_tarball(tarball_full_path, destination_directory=None, progress_update_callback=None):
    if destination_directory is None:
        destination_directory = tarball_full_path[:-8]
    log.debug("extracting %s\n  to %s", tarball_full_path, destination_directory)

    assert not lexists(destination_directory), destination_directory

    with tarfile.open(tarball_full_path) as t:
        members = t.getmembers()
        num_members = len(members)

        def members_with_progress():
            for q, member in enumerate(members):
                if progress_update_callback:
                    progress_update_callback(q / num_members)
                yield member

        t.extractall(path=destination_directory, members=members_with_progress())

    if sys.platform.startswith('linux') and os.getuid() == 0:
        # When extracting as root, tarfile will by restore ownership
        # of extracted files.  However, we want root to be the owner
        # (our implementation of --no-same-owner).
        for root, dirs, files in os.walk(destination_directory):
            for fn in files:
                p = join(root, fn)
                os.lchown(p, 0, 0)