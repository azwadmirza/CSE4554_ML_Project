def main():
  """Parse arguments, load link or layout metadata file and either sign
  metadata file or verify its signatures. """

  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description="""
Provides command line interface to sign in-toto link or layout metadata or
verify its signatures, with options to:

  * replace (default) or add signature(s):
    + layout metadata can be signed by multiple keys at once,
    + link metadata can only be signed by one key at a time.

  * write signed metadata to a specified path. If no output path is specified,
    + layout metadata is written to the path of the input file,
    + link metadata is written to '<name>.<keyid prefix>.link'.

  * verify signatures

Returns nonzero value on failure and zero otherwise.""")

  parser.epilog = """
examples:
  Append two signatures to 'unsigned.layout' file and write to 'root.layout'.

      {prog} -f unsigned.layout -k priv_key1 priv_key2 -o root.layout -a


  Replace signature in link file. And write to default filename, i.e.
  'package.<priv_key's keyid prefix>.link'.

      {prog} -f package.2f89b927.link -k priv_key


  Verify layout signed with 3 keys.

      {prog} -f root.layout -k pub_key0 pub_key1 pub_key2 --verify


  Sign layout with default gpg key in default gpg keyring.

      {prog} -f root.layout --gpg


  Verify layout with a gpg key identified by keyid '...439F3C2'.

      {prog} -f root.layout --verify \\
      --gpg 3BF8135765A07E21BD12BF89A5627F6BF439F3C2

""".format(prog=parser.prog)


  named_args = parser.add_argument_group("required named arguments")

  named_args.add_argument("-f", "--file", type=str, required=True,
      metavar="<path>", help=(
        "Path to link or layout file to be signed or verified."))

  parser.add_argument("-k", "--key", nargs="+", metavar="<path>", help=(
      "Path(s) to PEM formatted key file(s), used to sign the passed link or"
      " layout metadata or to verify its signatures."))

  parser.add_argument("-t", "--key-type", dest="key_type",
      type=str, choices=in_toto.util.SUPPORTED_KEY_TYPES,
      nargs="+", help=(
      "Specify the key-type of the keys specified by the '--key'"
      " option. Number of values should be the same as the number of keys"
      " specified by the '--key' option. If '--key-type' is not passed,"
      " default key_type of all keys is assumed to be \"rsa\"."))

  parser.add_argument("-g", "--gpg", nargs="*", metavar="<id>", help=(
      "GPG keyid used to sign the passed link or layout metadata or to verify"
      " its signatures. If passed without keyid, the default GPG key is"
      " used."))

  parser.add_argument("--gpg-home", dest="gpg_home", type=str,
      metavar="<path>", help=(
      "Path to GPG keyring to load GPG key identified by '--gpg' option.  If"
      " '--gpg-home' is not passed, the default GPG keyring is used."))

  # Only when signing
  parser.add_argument("-o", "--output", type=str, metavar="<path>",
      help=(
      "Path to store metadata file to be signed. If not passed, layout"
      " metadata is written to the path of the input file and link metadata is"
      " written to '<step name>.<keyid prefix>.link'"))

  # Only when signing
  parser.add_argument("-a", "--append", action="store_true",
      help=(
      "If passed, signatures are added rather than replacing existing"
      " signatures. This option is only availabe for layout metdata."))

  parser.add_argument("--verify", action="store_true",
      help="Verify signature(s) of passed link or layout metadata.")

  verbosity_args = parser.add_mutually_exclusive_group(required=False)
  verbosity_args.add_argument("-v", "--verbose", dest="verbose",
      help="Verbose execution.", action="store_true")

  verbosity_args.add_argument("-q", "--quiet", dest="quiet",
      help="Suppress all output.", action="store_true")

  parser.add_argument('--version', action='version',
                      version='{} {}'.format(parser.prog, __version__))

  args = parser.parse_args()

  LOG.setLevelVerboseOrQuiet(args.verbose, args.quiet)

  # Additional argparse sanitization
  # NOTE: This tool is starting to have many inter-dependent argument
  # restrictions. Maybe we should make it less sophisticated at some point.
  if args.verify and (args.append or args.output):
    parser.print_help()
    parser.error("conflicting arguments: don't specify any of"
        " 'append' or 'output' when verifying signatures")

  # Regular signing and GPG signing are mutually exclusive
  if (args.key is None) == (args.gpg is None):
    parser.print_help()
    parser.error("wrong arguments: specify either `--key PATH [PATH ...]`"
      " or `--gpg [KEYID [KEYID ...]]`")

  # For gpg verification we must specify a keyid (no default key is loaded)
  if args.verify and args.gpg is not None and len(args.gpg) < 1:
    parser.print_help()
    parser.error("missing arguments: specify at least one keyid for GPG"
      " signature verification (`--gpg KEYID ...`)")

  metadata = _load_metadata(args.file)

  # Specific command line argument restrictions if we deal with links
  if metadata.type_ == "link":
    # Above we check that it's either `--key ...` or `--gpg ...`
    # Here we check that it is not more than one in each case when dealing
    # with links
    link_error_message = ("Link metadata is associated with a"
        " single functionary and is usually namespaced accordingly:"
        " '<name>.<keyid>.link'.")

    if ((args.key is not None and len(args.key) > 1) or
        (args.gpg is not None and len(args.gpg) > 1)):
      parser.print_help()
      parser.error("too many arguments: {} Hence signing Link metadata"
          " with multiple keys is not allowed.".format(link_error_message))

    if args.append:
      parser.print_help()
      parser.error("wrong arguments: {}. Hence adding signatures to"
          " existing signatures on Link metadata is not allowed."
          .format(link_error_message))


  if args.verify:
    _verify_metadata(metadata, args)

  else:
    _sign_and_dump_metadata(metadata, args)