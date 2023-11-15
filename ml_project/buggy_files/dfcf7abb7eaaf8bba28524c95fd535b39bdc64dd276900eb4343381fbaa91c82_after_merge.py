def prepend_shebang_interpreter(args):
    # prepend interpreter directive (if any) to argument list
    #
    # When preparing virtual environments in a file container which has large
    # length, the system might not be able to invoke shebang scripts which
    # define interpreters beyond system limits (e.x. Linux as a limit of 128;
    # BINPRM_BUF_SIZE). This method can be used to check if the executable is
    # a script containing a shebang line. If so, extract the interpreter (and
    # possible optional argument) and prepend the values to the provided
    # argument list. tox will only attempt to read an interpreter directive of
    # a maximum size of 2048 bytes to limit excessive reading and support UNIX
    # systems which may support a longer interpret length.
    try:
        with open(args[0], "rb") as f:
            if f.read(1) == b"#" and f.read(1) == b"!":
                MAXINTERP = 2048
                interp = f.readline(MAXINTERP).rstrip().decode("UTF-8")
                interp_args = interp.split(None, 1)[:2]
                return interp_args + args
    except (UnicodeDecodeError, IOError):
        pass
    return args