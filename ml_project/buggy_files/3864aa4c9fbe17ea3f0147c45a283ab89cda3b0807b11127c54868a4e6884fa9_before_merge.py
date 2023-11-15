def path_shortener(path, short_paths):
    """ short_paths is 4-state:
    False: Never shorten the path
    True: Always shorten the path, create link if not existing
    None: Use shorten path only if already exists, not create
    """
    if short_paths is False or os.getenv("CONAN_USER_HOME_SHORT") == "None":
        return path
    link = os.path.join(path, CONAN_LINK)
    if os.path.exists(link):
        return load(link)
    elif short_paths is None:
        return path

    short_home = os.getenv("CONAN_USER_HOME_SHORT")
    if not short_home:
        drive = os.path.splitdrive(path)[0]
        short_home = drive + "/.conan"
    mkdir(short_home)

    # Workaround for short_home living in NTFS file systems. Give full control permission to current user to avoid
    # access problems in cygwin/msys2 windows subsystems when using short_home folder
    try:
        cmd = r'cacls %s /E /G "%s\%s":F' % (short_home, os.environ['USERDOMAIN'], os.environ['USERNAME'])
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)  # Ignoring any returned output, make command quiet
    except subprocess.CalledProcessError as e:
        # cmd can fail if trying to set ACL in non NTFS drives, ignoring it.
        pass

    redirect = tempfile.mkdtemp(dir=short_home, prefix="")
    # This "1" is the way to have a non-existing directory, so commands like
    # shutil.copytree() to it, works. It can be removed without compromising the
    # temp folder generator and conan-links consistency
    redirect = os.path.join(redirect, "1")
    save(link, redirect)
    return redirect