def in_toto_record_stop(step_name, product_list, signing_key=None,
    gpg_keyid=None, gpg_use_default=False, gpg_home=None,
    exclude_patterns=None, base_path=None, normalize_line_endings=False,
    lstrip_paths=None):
  """
  <Purpose>
    Finishes creating link metadata for a multi-part in-toto step.
    Loads unfinished link metadata file from disk, verifies
    that the file was signed with either the passed signing key, a gpg key
    identified by the passed gpg_keyid or the default gpg key.

    Then records products, updates unfinished Link object
    (products and signature), removes unfinished link file from and
    stores new link file to disk.

    One of signing_key, gpg_keyid or gpg_use_default has to be passed and it
    needs to be the same that was used with preceding in_toto_record_start.

  <Arguments>
    step_name:
            A unique name to relate link metadata with a step defined in the
            layout.
    product_list:
            List of file or directory paths that should be recorded as
            products.
    signing_key: (optional)
            If not None, link metadata is signed with this key.
            Format is securesystemslib.formats.KEY_SCHEMA
    gpg_keyid: (optional)
            If not None, link metadata is signed with a gpg key identified
            by the passed keyid.
    gpg_use_default: (optional)
            If True, link metadata is signed with default gpg key.
    gpg_home: (optional)
            Path to GPG keyring (if not set the default keyring is used).
    exclude_patterns: (optional)
            Artifacts matched by the pattern are excluded from the products
            sections in the resulting link.
    base_path: (optional)
            If passed, record products relative to base_path. Default is
            current working directory.
            NOTE: The base_path part of the recorded products is not included
            in the resulting preliminary link's product section.
    normalize_line_endings: (optional)
            If True, replaces windows and mac line endings with unix line
            endings before hashing products, for cross-platform support.
    lstrip_paths: (optional)
            If a prefix path is passed, the prefix is left stripped from
            the path of every artifact that contains the prefix.

  <Exceptions>
    ValueError if none of signing_key, gpg_keyid or gpg_use_default=True
        is passed.

    securesystemslib.FormatError if a signing_key is passed and does not match
        securesystemslib.formats.KEY_SCHEMA or a gpg_keyid is passed and does
        not match securesystemslib.formats.KEYID_SCHEMA, or exclude_patterns
        are passed and don't match securesystemslib.formats.NAMES_SCHEMA, or
        base_path is passed and does not match
        securesystemslib.formats.PATH_SCHEMA or is not a directory.

    LinkNotFoundError if gpg is used for signing and the corresponding
        preliminary link file can not be found in the current working directory

    SignatureVerificationError:
        If the signature of the preliminary link file is invalid.

    securesystemslib.gpg.exceptions.KeyExpirationError:
        If the key used to verify the signature of the preliminary link file is
        an expired gpg key.

    securesystemslib.gpg.exceptions.CommandError:
        If gpg is used for signing and the command exits with a non-zero code.

  <Side Effects>
    Writes newly created link metadata file to disk using the filename scheme
    from link.FILENAME_FORMAT
    Removes unfinished link file link.UNFINISHED_FILENAME_FORMAT from disk

  <Returns>
    None.

  """
  LOG.info("Stop recording '{}'...".format(step_name))

  # Check that we have something to sign and if the formats are right
  if not signing_key and not gpg_keyid and not gpg_use_default:
    raise ValueError("Pass either a signing key, a gpg keyid or set"
        " gpg_use_default to True")

  if signing_key:
    _check_match_signing_key(signing_key)
  if gpg_keyid:
    securesystemslib.formats.KEYID_SCHEMA.check_match(gpg_keyid)

  if exclude_patterns:
    securesystemslib.formats.NAMES_SCHEMA.check_match(exclude_patterns)

  if base_path:
    securesystemslib.formats.PATH_SCHEMA.check_match(base_path)

  # Load preliminary link file
  # If we have a signing key we can use the keyid to construct the name
  if signing_key:
    unfinished_fn = UNFINISHED_FILENAME_FORMAT.format(step_name=step_name,
        keyid=signing_key["keyid"])

  # FIXME: Currently there is no way to know the default GPG key's keyid and
  # so we glob for preliminary link files
  else:
    unfinished_fn_glob = UNFINISHED_FILENAME_FORMAT_GLOB.format(
        step_name=step_name, pattern="*")
    unfinished_fn_list = glob.glob(unfinished_fn_glob)

    if not len(unfinished_fn_list):
      raise in_toto.exceptions.LinkNotFoundError("Could not find a preliminary"
          " link for step '{}' in the current working directory.".format(
          step_name))

    if len(unfinished_fn_list) > 1:
      raise in_toto.exceptions.LinkNotFoundError("Found more than one"
          " preliminary links for step '{}' in the current working directory:"
          " {}. We need exactly one to stop recording.".format(
          step_name, ", ".join(unfinished_fn_list)))

    unfinished_fn = unfinished_fn_list[0]

  LOG.info("Loading preliminary link metadata '{}'...".format(unfinished_fn))
  link_metadata = Metablock.load(unfinished_fn)

  # The file must have been signed by the same key
  # If we have a signing_key we use it for verification as well
  if signing_key:
    LOG.info(
        "Verifying preliminary link signature using passed signing key...")
    keyid = signing_key["keyid"]
    verification_key = signing_key

  elif gpg_keyid:
    LOG.info("Verifying preliminary link signature using passed gpg key...")
    gpg_pubkey = securesystemslib.gpg.functions.export_pubkey(
        gpg_keyid, gpg_home)
    keyid = gpg_pubkey["keyid"]
    verification_key = gpg_pubkey

  else: # must be gpg_use_default
    # FIXME: Currently there is no way to know the default GPG key's keyid
    # before signing. As a workaround we extract the keyid of the preliminary
    # Link file's signature and try to export a pubkey from the gpg
    # keyring. We do this even if a gpg_keyid was specified, because gpg
    # accepts many different ids (mail, name, parts of an id, ...) but we
    # need a specific format.
    LOG.info("Verifying preliminary link signature using default gpg key...")
    keyid = link_metadata.signatures[0]["keyid"]
    gpg_pubkey = securesystemslib.gpg.functions.export_pubkey(
        keyid, gpg_home)
    verification_key = gpg_pubkey

  link_metadata.verify_signature(verification_key)

  # Record products if a product path list was passed
  if product_list:
    LOG.info("Recording products '{}'...".format(", ".join(product_list)))

  link_metadata.signed.products = record_artifacts_as_dict(
      product_list, exclude_patterns=exclude_patterns, base_path=base_path,
      follow_symlink_dirs=True, normalize_line_endings=normalize_line_endings,
      lstrip_paths=lstrip_paths)

  link_metadata.signatures = []
  if signing_key:
    LOG.info("Updating signature with key '{:.8}...'...".format(keyid))
    link_metadata.sign(signing_key)

  else: # gpg_keyid or gpg_use_default
    # In both cases we use the keyid we got from verifying the preliminary
    # link signature above.
    LOG.info("Updating signature with gpg key '{:.8}...'...".format(keyid))
    link_metadata.sign_gpg(keyid, gpg_home)

  fn = FILENAME_FORMAT.format(step_name=step_name, keyid=keyid)
  LOG.info("Storing link metadata to '{}'...".format(fn))
  link_metadata.dump(fn)

  LOG.info("Removing unfinished link metadata '{}'...".format(unfinished_fn))
  os.remove(unfinished_fn)