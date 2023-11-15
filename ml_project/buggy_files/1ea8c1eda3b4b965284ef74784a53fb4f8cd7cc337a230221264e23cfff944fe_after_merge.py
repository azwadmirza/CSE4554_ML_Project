def append(path, *args):
    '''
    .. versionadded:: 0.9.5

    Append text to the end of a file

    CLI Example:

    .. code-block:: bash

        salt '*' file.append /etc/motd \\
                "With all thine offerings thou shalt offer salt." \\
                "Salt is what makes things taste bad when it isn't in them."
    '''
    # Largely inspired by Fabric's contrib.files.append()

    with salt.utils.fopen(path, "r+") as ofile:
        # Make sure we have a newline at the end of the file
        try:
            ofile.seek(-1, os.SEEK_END)
        except IOError as exc:
            if exc.errno == errno.EINVAL:
                # Empty file, simply append lines at the beginning of the file
                pass
            else:
                raise
        else:
            if ofile.read(1) != '\n':
                ofile.seek(0, os.SEEK_END)
                ofile.write('\n')
            else:
                ofile.seek(0, os.SEEK_END)
        # Append lines
        for line in args:
            ofile.write('{0}\n'.format(line))

    return 'Wrote {0} lines to "{1}"'.format(len(args), path)