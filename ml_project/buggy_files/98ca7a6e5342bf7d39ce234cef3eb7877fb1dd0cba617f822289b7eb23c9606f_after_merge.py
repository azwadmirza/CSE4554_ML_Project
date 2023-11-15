def in_toto_record_start(step_name, material_list, signing_key=None,
    gpg_keyid=None, gpg_use_default=False, gpg_home=None,
    exclude_patterns=None, base_path=None, record_environment=False,
    normalize_line_endings=False, lstrip_paths=None):
  """
  <Purpose>
    Starts creating link metadata for a multi-part in-toto step. I.e.
    records passed materials, creates link meta data object from it, signs it
    with passed signing_key, gpg key identified by the passed gpg_keyid
    or the default gpg key and stores it to disk under
    UNFINISHED_FILENAME_FORMAT.

    One of signing_key, gpg_keyid or gpg_use_default has to be passed.

  <Arguments>
    step_name:
            A unique name to relate link metadata with a step defined in the
            layout.
    material_list:
            List of file or directory paths that should be recorded as
            materials.
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
            Artifacts matched by the pattern are excluded from the materials
            section in the resulting preliminary link.
    base_path: (optional)
            If passed, record materials relative to base_path. Default is
            current working directory.
            NOTE: The base_path part of the recorded materials is not included
            in the resulting preliminary link's material section.
    record_environment: (optional)
            if values such as workdir should be recorded  on the environment
            dictionary (false by default)
    normalize_line_endings: (optional)
            If True, replaces windows and mac line endings with unix line
            endings before hashing materials, for cross-platform support.
    lstrip_paths: (optional)
            If a prefix path is passed, the prefix is left stripped from
            the path of every artifact that contains the prefix.

  <Exceptions>
    ValueError if none of signing_key, gpg_keyid or gpg_use_default=True
        is passed.

    securesystemslib.FormatError if a signing_key is passed and does not match
        securesystemslib.formats.KEY_SCHEMA or a gpg_keyid is passed and does
        not match securesystemslib.formats.KEYID_SCHEMA or exclude_patterns
        are passed and don't match securesystemslib.formats.NAMES_SCHEMA, or
        base_path is passed and does not match
        securesystemslib.formats.PATH_SCHEMA or is not a directory.

    securesystemslib.gpg.exceptions.CommandError:
        If gpg is used for signing and the command exits with a non-zero code.

  <Side Effects>
    Writes newly created link metadata file to disk using the filename scheme
    from link.UNFINISHED_FILENAME_FORMAT

  <Returns>
    None.

  """
  LOG.info("Start recording '{}'...".format(step_name))

  # Fail if there is no signing key arg at all
  if not signing_key and not gpg_keyid and not gpg_use_default:
    raise ValueError("Pass either a signing key, a gpg keyid or set"
        " gpg_use_default to True!")

  # Check key formats to fail early
  if signing_key:
    _check_match_signing_key(signing_key)
  if gpg_keyid:
    securesystemslib.formats.KEYID_SCHEMA.check_match(gpg_keyid)

  if exclude_patterns:
    securesystemslib.formats.NAMES_SCHEMA.check_match(exclude_patterns)

  if base_path:
    securesystemslib.formats.PATH_SCHEMA.check_match(base_path)

  if material_list:
    LOG.info("Recording materials '{}'...".format(", ".join(material_list)))

  materials_dict = record_artifacts_as_dict(material_list,
      exclude_patterns=exclude_patterns, base_path=base_path,
      follow_symlink_dirs=True, normalize_line_endings=normalize_line_endings,
      lstrip_paths=lstrip_paths)

  LOG.info("Creating preliminary link metadata...")
  environment = {}
  if record_environment:
    environment['workdir'] = os.getcwd().replace('\\', '/')

  link = in_toto.models.link.Link(name=step_name,
          materials=materials_dict, products={}, command=[], byproducts={},
          environment=environment)

  link_metadata = Metablock(signed=link)

  if signing_key:
    LOG.info("Signing link metadata using passed key...")
    signature = link_metadata.sign(signing_key)

  elif gpg_keyid:
    LOG.info("Signing link metadata using passed GPG keyid...")
    signature = link_metadata.sign_gpg(gpg_keyid, gpg_home=gpg_home)

  else:  # (gpg_use_default)
    LOG.info("Signing link metadata using default GPG key ...")
    signature = link_metadata.sign_gpg(gpg_keyid=None, gpg_home=gpg_home)

  # We need the signature's keyid to write the link to keyid infix'ed filename
  signing_keyid = signature["keyid"]

  unfinished_fn = UNFINISHED_FILENAME_FORMAT.format(step_name=step_name,
    keyid=signing_keyid)

  LOG.info(
      "Storing preliminary link metadata to '{}'...".format(unfinished_fn))
  link_metadata.dump(unfinished_fn)