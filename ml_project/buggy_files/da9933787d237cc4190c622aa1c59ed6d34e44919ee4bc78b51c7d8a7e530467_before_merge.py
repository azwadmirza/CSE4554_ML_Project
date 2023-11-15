def wipe_path(pathname, idle=False):
    """Wipe the free space in the path
    This function uses an iterator to update the GUI."""

    def temporaryfile():
        # reference
        # http://en.wikipedia.org/wiki/Comparison_of_file_systems#Limits
        maxlen = 185
        f = None
        while True:
            try:
                f = tempfile.NamedTemporaryFile(
                    dir=pathname, suffix=__random_string(maxlen), delete=False)
                # In case the application closes prematurely, make sure this
                # file is deleted
                atexit.register(
                    delete, f.name, allow_shred=False, ignore_missing=True)
                break
            except OSError as e:
                if e.errno in (errno.ENAMETOOLONG, errno.ENOSPC, errno.ENOENT, errno.EINVAL):
                    # ext3 on Linux 3.5 returns ENOSPC if the full path is greater than 264.
                    # Shrinking the size helps.

                    # Microsoft Windows returns ENOENT "No such file or directory"
                    # or EINVAL "Invalid argument"
                    # when the path is too long such as %TEMP% but not in C:\
                    if maxlen > 5:
                        maxlen -= 5
                        continue
                raise
        return f

    def estimate_completion():
        """Return (percent, seconds) to complete"""
        remaining_bytes = free_space(pathname)
        done_bytes = start_free_bytes - remaining_bytes
        if done_bytes < 0:
            # maybe user deleted large file after starting wipe
            done_bytes = 0
        if 0 == start_free_bytes:
            done_percent = 0
        else:
            done_percent = 1.0 * done_bytes / (start_free_bytes + 1)
        done_time = time.time() - start_time
        rate = done_bytes / (done_time + 0.0001)  # bytes per second
        remaining_seconds = int(remaining_bytes / (rate + 0.0001))
        return 1, done_percent, remaining_seconds

    logger.debug(_("Wiping path: %s") % pathname)
    files = []
    total_bytes = 0
    start_free_bytes = free_space(pathname)
    start_time = time.time()
    # Because FAT32 has a maximum file size of 4,294,967,295 bytes,
    # this loop is sometimes necessary to create multiple files.
    while True:
        try:
            logger.debug(
                _('Creating new, temporary file for wiping free space.'))
            f = temporaryfile()
        except OSError as e:
            # Linux gives errno 24
            # Windows gives errno 28 No space left on device
            if e.errno in (errno.EMFILE, errno.ENOSPC):
                break
            else:
                raise
        last_idle = time.time()
        # Write large blocks to quickly fill the disk.
        blanks = b'\0' * 65536
        while True:
            try:
                f.write(blanks)
            except IOError as e:
                if e.errno == errno.ENOSPC:
                    if len(blanks) > 1:
                        # Try writing smaller blocks
                        blanks = blanks[0:len(blanks) // 2]
                    else:
                        break
                elif e.errno == errno.EFBIG:
                    break
                else:
                    raise
            if idle and (time.time() - last_idle) > 2:
                # Keep the GUI responding, and allow the user to abort.
                # Also display the ETA.
                yield estimate_completion()
                last_idle = time.time()
        # Write to OS buffer
        try:
            f.flush()
        except IOError as e:
            # IOError: [Errno 28] No space left on device
            # seen on Microsoft Windows XP SP3 with ~30GB free space but
            # not on another XP SP3 with 64MB free space
            if not e.errno == errno.ENOSPC:
                logger.error(
                    _("Error #%d when flushing the file buffer." % e.errno))

        os.fsync(f.fileno())  # write to disk
        # Remember to delete
        files.append(f)
        # For statistics
        total_bytes += f.tell()
        # If no bytes were written, then quit.
        # See https://github.com/bleachbit/bleachbit/issues/502
        if start_free_bytes - total_bytes < 2: # Modified by Marvin to fix the issue #1051 [12/06/2020]
            break
    # sync to disk
    sync()
    # statistics
    elapsed_sec = time.time() - start_time
    rate_mbs = (total_bytes / (1000 * 1000)) / elapsed_sec
    logger.info(_('Wrote {files:,} files and {bytes:,} bytes in {seconds:,} seconds at {rate:.2f} MB/s').format(
                files=len(files), bytes=total_bytes, seconds=int(elapsed_sec), rate=rate_mbs))
    # how much free space is left (should be near zero)
    if 'posix' == os.name:
        stats = os.statvfs(pathname)
        logger.info(_("{bytes:,} bytes and {inodes:,} inodes available to non-super-user").format(
                    bytes=stats.f_bsize * stats.f_bavail, inodes=stats.f_favail))
        logger.info(_("{bytes:,} bytes and {inodes:,} inodes available to super-user").format(
                    bytes=stats.f_bsize * stats.f_bfree, inodes=stats.f_ffree))
    # truncate and close files
    for f in files:
        truncate_f(f)

        while True:
            try:
                # Nikita: I noticed a bug that prevented file handles from
                # being closed on FAT32. It sometimes takes two .close() calls
                # to do actually close (and therefore delete) a temporary file
                f.close()
                break
            except IOError as e:
                if e.errno == 0:
                    logger.debug(
                        _("Handled unknown error #0 while truncating file."))
                    time.sleep(0.1)
        # explicitly delete
        delete(f.name, ignore_missing=True)