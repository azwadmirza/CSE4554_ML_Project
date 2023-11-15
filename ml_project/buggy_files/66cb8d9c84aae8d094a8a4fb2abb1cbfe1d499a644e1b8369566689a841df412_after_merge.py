def color_file(file_path: str, path_stat: os.stat_result) -> (Color, str):
    """Determine color to use for file *approximately* as ls --color would, given lstat() results and its name.

    Parameters
    ----------
    file_path:
        relative path of file (as user typed it).
    path_stat:
        lstat() results for file_path.

    Returns
    -------
        color token, color_key

    Notes
    -----

    * implementation follows one authority:
      https://github.com/coreutils/coreutils/blob/master/src/ls.c#L4879
    * except:
    1. does not return 'mi' symlink to missing file unless ln=target,
      because caller provides an existing file.
    2. in dircolors, setting type code to '0 or '00' bypasses that test and proceeds to others.
       In our implementation, setting code to '00' paints the file with no color.
       This is arguably a bug.
    3. dircolors with ln=target only colors links to fundamental types, not to *.zoo 
       (file extension patterns). This function will paint the link with the ultimate file type color.
       This is arguably better for the user typing a filename on the command line.
    """

    lsc = builtins.__xonsh__.env["LS_COLORS"]
    color_key = "fi"

    # if ln=target, get name of target (next link only) and its lstat_result
    if lsc.is_target("ln") and stat.S_ISLNK(path_stat.st_mode):
        try:
            file_path = os.readlink(
                file_path
            )  # next hop in symlink chain, just like ls
            path_stat = os.lstat(file_path)  # and work with its properties
        except FileNotFoundError:
            color_key = "mi"  # early exit
            ret_color_token = file_color_tokens.get(color_key, Text)
            return ret_color_token, color_key

    mode = path_stat.st_mode

    if stat.S_ISREG(mode):
        if mode & stat.S_ISUID:
            color_key = "su"
        elif mode & stat.S_ISGID:
            color_key = "sg"
        else:
            cap = os_listxattr(file_path, follow_symlinks=False)
            if cap and "security.capability" in cap:  # protect None return on some OS?
                color_key = "ca"
            elif stat.S_IMODE(mode) & (stat.S_IXUSR + stat.S_IXGRP + stat.S_IXOTH):
                color_key = "ex"
            elif path_stat.st_nlink > 1:
                color_key = "mh"
            else:
                color_key = "fi"
    elif stat.S_ISDIR(mode):  # ls --color doesn't colorize sticky or ow if not dirs...
        color_key = "di"
        if (mode & stat.S_ISVTX) and (mode & stat.S_IWOTH):
            color_key = "tw"
        elif mode & stat.S_IWOTH:
            color_key = "ow"
        elif mode & stat.S_ISVTX:
            color_key = "st"
    elif stat.S_ISLNK(mode):
        color_key = "ln"
    elif stat.S_ISFIFO(mode):
        color_key = "pi"
    elif stat.S_ISSOCK(mode):
        color_key = "so"
    elif stat.S_ISBLK(mode):
        color_key = "bd"
    elif stat.S_ISCHR(mode):
        color_key = "cd"
    elif stat.S_ISDOOR(mode):
        color_key = "do"
    else:
        color_key = "or"  # any other type --> orphan

    if color_key == "fi":  # if still normal file -- try color by file extension.
        match = color_file_extension_RE.match(file_path)
        if match:
            ext = "*" + match.group(1)  # look for *.<fileExtension> coloring
            if ext in lsc:
                color_key = ext

    ret_color_token = file_color_tokens.get(color_key, Text)

    return ret_color_token, color_key