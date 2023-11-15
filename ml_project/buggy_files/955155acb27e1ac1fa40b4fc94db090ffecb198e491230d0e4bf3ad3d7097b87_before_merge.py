def main(args):
  parser, resolver_options_builder = configure_clp()

  try:
    separator = args.index('--')
    args, cmdline = args[:separator], args[separator + 1:]
  except ValueError:
    args, cmdline = args, []

  options, reqs = parser.parse_args(args=args)
  if options.pex_root:
    ENV.set('PEX_ROOT', options.pex_root)
  else:
    options.pex_root = ENV.PEX_ROOT  # If option not specified fallback to env variable.

  options.cache_dir = make_relative_to_root(options.cache_dir)
  options.interpreter_cache_dir = make_relative_to_root(options.interpreter_cache_dir)

  with ENV.patch(PEX_VERBOSE=str(options.verbosity)):
    with TRACER.timed('Building pex'):
      pex_builder = build_pex(reqs, options, resolver_options_builder)

    if options.pex_name is not None:
      log('Saving PEX file to %s' % options.pex_name, v=options.verbosity)
      tmp_name = options.pex_name + '~'
      safe_delete(tmp_name)
      pex_builder.build(tmp_name)
      os.rename(tmp_name, options.pex_name)
      return 0

    if options.platform != Platform.current():
      log('WARNING: attempting to run PEX with differing platform!')

    pex_builder.freeze()

    log('Running PEX file at %s with args %s' % (pex_builder.path(), cmdline), v=options.verbosity)
    pex = PEX(pex_builder.path(), interpreter=pex_builder.interpreter)
    sys.exit(pex.run(args=list(cmdline)))