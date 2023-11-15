def process(args):
    """Run the function in args.name given arguments in args.argfile.
    """
    # Set environment to standard to use periods for decimals and avoid localization
    locale_to_use = utils.get_locale()
    os.environ["LC_ALL"] = locale_to_use
    os.environ["LC"] = locale_to_use
    os.environ["LANG"] = locale_to_use
    setpath.prepend_bcbiopath()
    try:
        fn = getattr(multitasks, args.name)
    except AttributeError:
        raise AttributeError("Did not find exposed function in bcbio.distributed.multitasks named '%s'" % args.name)
    if args.moreargs or args.raw:
        fnargs = [args.argfile] + args.moreargs
        work_dir = None
        argfile = None
    else:
        with open(args.argfile) as in_handle:
            fnargs = yaml.safe_load(in_handle)
        work_dir = os.path.dirname(args.argfile)
        fnargs = config_utils.merge_resources(fnargs)
        argfile = args.outfile if args.outfile else "%s-out%s" % os.path.splitext(args.argfile)
    if not work_dir:
        work_dir = os.getcwd()
    if len(fnargs) > 0 and fnargs[0] == "cwl":
        fnargs, parallel, out_keys, input_files = _world_from_cwl(args.name, fnargs[1:], work_dir)
        # Can remove this awkward Docker merge when we do not need custom GATK3 installs
        fnargs = config_utils.merge_resources(fnargs)
        argfile = os.path.join(work_dir, "cwl.output.json")
    else:
        parallel, out_keys, input_files = None, {}, []
    with utils.chdir(work_dir):
        with contextlib.closing(log.setup_local_logging(parallel={"wrapper": "runfn"})):
            try:
                out = fn(*fnargs)
            except:
                logger.exception()
                raise
            finally:
                # Clean up any copied and unpacked workflow inputs, avoiding extra disk usage
                wf_input_dir = os.path.join(work_dir, "wf-inputs")
                if os.path.exists(wf_input_dir) and os.path.isdir(wf_input_dir):
                    shutil.rmtree(wf_input_dir)
    if argfile:
        try:
            _write_out_argfile(argfile, out, fnargs, parallel, out_keys, input_files, work_dir)
        except:
            logger.exception()
            raise