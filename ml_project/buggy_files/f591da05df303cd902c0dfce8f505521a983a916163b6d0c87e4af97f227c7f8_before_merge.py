def main(fp=sys.stderr):
    """
    Paramters (internal use only)
    ---------
    fp  : file-like object for tqdm
    """
    try:
        log = sys.argv.index('--log')
    except ValueError:
        logLevel = 'INFO'
    else:
        # sys.argv.pop(log)
        # logLevel = sys.argv.pop(log)
        logLevel = sys.argv[log + 1]
    logging.basicConfig(level=getattr(logging, logLevel),
        format="%(levelname)s:%(module)s:%(lineno)d:%(message)s")
    log = logging.getLogger(__name__)

    d = tqdm.__init__.__doc__ + CLI_EXTRA_DOC

    opt_types = dict(RE_OPTS.findall(d))
    # opt_types['delim'] = 'chr'

    for o in UNSUPPORTED_OPTS:
        opt_types.pop(o)

    log.debug(sorted(opt_types.items()))

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

    argv = RE_SHLEX.split(' '.join(["tqdm"] + sys.argv[1:]))
    opts = dict(zip(argv[1::2], argv[2::2]))

    log.debug(opts)
    opts.pop('log', True)

    tqdm_args = {'file': fp}
    try:
        for (o, v) in opts.items():
            try:
                tqdm_args[o] = cast(v, opt_types[o])
            except KeyError as e:
                raise TqdmKeyError(str(e))
        log.debug('args:' + str(tqdm_args))
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
            tqdm_args.setdefault('unit', 'B')
            tqdm_args.setdefault('unit_scale', True)
            tqdm_args.setdefault('unit_divisor', 1024)
            log.debug(tqdm_args)
            with tqdm(**tqdm_args) as t:
                posix_pipe(sys.stdin, sys.stdout,
                           '', buf_size, t.update)
        elif delim == '\n':
            log.debug(tqdm_args)
            for i in tqdm(sys.stdin, **tqdm_args):
                sys.stdout.write(i)
        else:
            log.debug(tqdm_args)
            with tqdm(**tqdm_args) as t:
                posix_pipe(sys.stdin, sys.stdout,
                           delim, buf_size, t.update)