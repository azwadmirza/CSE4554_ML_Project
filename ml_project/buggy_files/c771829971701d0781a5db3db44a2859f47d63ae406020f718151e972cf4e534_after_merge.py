def process_truffle(dirname, args, detector_classes, printer_classes):
    # Truffle on windows has naming conflicts where it will invoke truffle.js directly instead
    # of truffle.cmd (unless in powershell or git bash). The cleanest solution is to explicitly call
    # truffle.cmd. Reference:
    # https://truffleframework.com/docs/truffle/reference/configuration#resolving-naming-conflicts-on-windows
    if not args.ignore_truffle_compile:
        truffle_base_command = "truffle" if platform.system() != 'Windows' else "truffle.cmd"
        cmd = [truffle_base_command, 'compile']
        if args.truffle_version:
            cmd = ['npx',args.truffle_version,'compile']
        elif os.path.isfile('package.json'):
            with open('package.json') as f:
                    package = json.load(f)
                    if 'devDependencies' in package:
                        if 'truffle' in package['devDependencies']:
                            version = package['devDependencies']['truffle']
                            if version.startswith('^'):
                                version = version[1:]
                            truffle_version = 'truffle@{}'.format(version)
                            cmd = ['npx', truffle_version,'compile']
        logger.info("'{}' running (use --truffle-version truffle@x.x.x to use specific version)".format(' '.join(cmd)))
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        stdout, stderr = stdout.decode(), stderr.decode()  # convert bytestrings to unicode strings

        logger.info(stdout)

        if stderr:
            logger.error(stderr)

    slither = Slither(dirname,
                      solc=args.solc,
                      disable_solc_warnings=args.disable_solc_warnings,
                      solc_arguments=args.solc_args,
                      is_truffle=True,
                      filter_paths=parse_filter_paths(args),
                      triage_mode=args.triage_mode)

    return _process(slither, detector_classes, printer_classes)