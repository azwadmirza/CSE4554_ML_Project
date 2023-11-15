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

    with salt.utils.fopen(path, "a") as ofile:
        for line in args:
            ofile.write('{0}\n'.format(line))

    return 'Wrote {0} lines to "{1}"'.format(len(args), path)