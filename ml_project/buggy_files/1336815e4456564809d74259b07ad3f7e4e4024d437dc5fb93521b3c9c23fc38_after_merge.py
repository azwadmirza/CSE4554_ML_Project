def _sign_and_dump_metadata(metadata, args):
  """
  <Purpose>
    Internal method to sign link or layout metadata and dump it to disk.

  <Arguments>
    metadata:
            Metablock object (contains Link or Layout object)
    args:
            see argparser

  <Exceptions>
    SystemExit(0) if signing is successful
    SystemExit(2) if any exception occurs

  """

  try:
    if not args.append:
      metadata.signatures = []

    signature = None
    # If the cli tool was called with `--gpg [KEYID ...]` `args.gpg` is
    # a list (not None) and we will try to sign with gpg.
    # If `--gpg-home` was not set, args.gpg_home is None and the signer tries
    # to use the default gpg keyring.
    if args.gpg is not None:
      # If `--gpg` was passed without argument we sign with the default key
      # Excluded so that coverage does not vary in different test environments
      if len(args.gpg) == 0: # pragma: no cover
        signature = metadata.sign_gpg(gpg_keyid=None, gpg_home=args.gpg_home)

      # Otherwise we sign with each passed keyid
      for keyid in args.gpg:
        securesystemslib.formats.KEYID_SCHEMA.check_match(keyid)
        signature = metadata.sign_gpg(gpg_keyid=keyid, gpg_home=args.gpg_home)

    # Alternatively we iterate over passed private key paths `--key KEYPATH
    # ...` load the corresponding key from disk and sign with it
    elif args.key is not None: # pragma: no branch

      if args.key_type is None:
        args.key_type = [util.KEY_TYPE_RSA] * len(args.key)

      if len(args.key_type) != len(args.key):
        raise securesystemslib.exceptions.FormatError(
          "number of key_types should match with the number"
          " of keys specified")

      for idx, key_path in enumerate(args.key):
        key = util.import_private_key_from_file(key_path, args.key_type[idx])
        signature = metadata.sign(key)

    # If `--output` was specified we store the signed link or layout metadata
    # to that location no matter what
    if args.output:
      out_path = args.output

    # Otherwise, in case of links, we build the filename using the link/step
    # name and the keyid of the created signature (there is only one for links)
    elif metadata.type_ == "link":
      securesystemslib.formats.ANY_SIGNATURE_SCHEMA.check_match(signature)
      keyid = signature["keyid"]
      out_path = FILENAME_FORMAT.format(step_name=metadata.signed.name,
          keyid=keyid)

    # In case of layouts we just override the input file.
    elif metadata.type_ == "layout": # pragma: no branch
      out_path = args.file

    LOG.info("Dumping {0} to '{1}'...".format(metadata.type_, out_path))

    metadata.dump(out_path)
    sys.exit(0)

  except Exception as e:
    LOG.error("The following error occurred while signing: "
        "{}".format(e))
    sys.exit(2)