def main(fp=sys.stderr):
    """
    Paramters (internal use only)
    ---------
    fp  : file-like object for tqdm
    """
    d = tqdm.__init__.__doc__ + CLI_EXTRA_DOC

    opt_types = dict(RE_OPTS.findall(d))

    for o in UNSUPPORTED_OPTS:
        opt_types.pop(o)

    # d = RE_OPTS.sub(r'  --\1=<\1>  : \2', d)
    split = RE_OPTS.split(d)
    opt_types_desc = zip(split[1::3], split[2::3], split[3::3])
    d = ''.join('\n  --{0}=<{0}>  : {1}{2}'.format(*otd)
                for otd in opt_types_desc if otd[0] not in UNSUPPORTED_OPTS)

    d = """Usage:
  tqdm [--help | options]

Options:
  -h, --help     Print this help and exit
  -v, --version  Print version and exit

""" + d.strip('\n') + '\n'

    # opts = docopt(d, version=__version__)
    if any(v in sys.argv for v in ('-v', '--version')):
        sys.stdout.write(__version__ + '\n')
        sys.exit(0)
    elif any(v in sys.argv for v in ('-h', '--help')):
        sys.stdout.write(d + '\n')
        sys.exit(0)

    argv = RE_SHLEX.split(' '.join(sys.argv))
    opts = dict(zip(argv[1::2], argv[2::2]))

    tqdm_args = {'file': fp}
    try:
        for (o, v) in opts.items():
            try:
                tqdm_args[o] = cast(v, opt_types[o])
            except KeyError as e:
                raise TqdmKeyError(str(e))
        # fp.write('\ndebug | args: ' + str(tqdm_args) + '\n')
    except:
        fp.write('\nError:\nUsage:\n  tqdm [--help | options]\n')
        for i in sys.stdin:
            sys.stdout.write(i)
        raise
    else:
        buf_size = tqdm_args.pop('buf_size', 256)
        delim = tqdm_args.pop('delim', '\n')
        delim_per_char = tqdm_args.pop('bytes', False)
        if delim_per_char:
            with tqdm(**tqdm_args) as t:
                posix_pipe(sys.stdin, sys.stdout,
                           '', buf_size, t.update)
        elif delim == '\n':
            for i in tqdm(sys.stdin, **tqdm_args):
                sys.stdout.write(i)
        else:
            with tqdm(**tqdm_args) as t:
                posix_pipe(sys.stdin, sys.stdout,
                           delim, buf_size, t.update)