def in_toto_run(name, material_list, product_list, link_cmd_args,
    record_streams=False, signing_key=None, gpg_keyid=None,
    gpg_use_default=False, gpg_home=None, exclude_patterns=None,
    base_path=None, compact_json=False, record_environment=False,
    normalize_line_endings=False, lstrip_paths=None):
  """
  <Purpose>
    Calls functions in this module to run the command passed as link_cmd_args
    argument and to store materials, products, by-products and environment
    information into a link metadata file.

    The link metadata file is signed either with the passed signing_key, or
    a gpg key identified by the passed gpg_keyid or with the default gpg
    key if gpg_use_default is True.

    Even if multiple key parameters are passed, only one key is used for
    signing (in above order of precedence).

    The link file is dumped to `link.FILENAME_FORMAT` using the signing key's
    keyid.

    If no key parameter is passed the link is neither signed nor dumped.

  <Arguments>
    name:
            A unique name to relate link metadata with a step or inspection
            defined in the layout.
    material_list:
            List of file or directory paths that should be recorded as
            materials.
    product_list:
            List of file or directory paths that should be recorded as
            products.
    link_cmd_args:
            A list where the first element is a command and the remaining
            elements are arguments passed to that command.
    record_streams: (optional)
            A bool that specifies whether to redirect standard output and
            and standard error to a temporary file which is returned to the
            caller (True) or not (False).
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
            and products sections in the resulting link.
    base_path: (optional)
            If passed, record artifacts relative to base_path. Default is
            current working directory.
            NOTE: The base_path part of the recorded material is not included
            in the resulting preliminary link's material/product sections.
    compact_json: (optional)
            Whether or not to use the most compact json representation.
    record_environment: (optional)
            if values such as workdir should be recorded  on the environment
            dictionary (false by default)
    normalize_line_endings: (optional)
            If True, replaces windows and mac line endings with unix line
            endings before hashing materials and products, for cross-platform
            support.
    lstrip_paths: (optional)
            If a prefix path is passed, the prefix is left stripped from
            the path of every artifact that contains the prefix.

  <Exceptions>
    securesystemslib.FormatError if a signing_key is passed and does not match
        securesystemslib.formats.KEY_SCHEMA or a gpg_keyid is passed and does
        not match securesystemslib.formats.KEYID_SCHEMA or exclude_patterns
        are passed and don't match securesystemslib.formats.NAMES_SCHEMA, or
        base_path is passed and does not match
        securesystemslib.formats.PATH_SCHEMA or is not a directory.

    securesystemslib.gpg.exceptions.CommandError:
        If gpg is used for signing and the command exits with a non-zero code.

  <Side Effects>
    If a key parameter is passed for signing, the newly created link metadata
    file is written to disk using the filename scheme: `link.FILENAME_FORMAT`

  <Returns>
    Newly created Metablock object containing a Link object

  """
  LOG.info("Running '{}'...".format(name))

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

  if link_cmd_args:
    LOG.info("Running command '{}'...".format(" ".join(link_cmd_args)))
    byproducts = execute_link(link_cmd_args, record_streams)
  else:
    byproducts = {}

  if product_list:
    securesystemslib.formats.PATHS_SCHEMA.check_match(product_list)
    LOG.info("Recording products '{}'...".format(", ".join(product_list)))

  products_dict = record_artifacts_as_dict(product_list,
      exclude_patterns=exclude_patterns, base_path=base_path,
      follow_symlink_dirs=True, normalize_line_endings=normalize_line_endings,
      lstrip_paths=lstrip_paths)

  LOG.info("Creating link metadata...")
  environment = {}
  if record_environment:
    environment['workdir'] = os.getcwd().replace('\\', '/')

  link = in_toto.models.link.Link(name=name,
      materials=materials_dict, products=products_dict, command=link_cmd_args,
      byproducts=byproducts, environment=environment)

  link_metadata = Metablock(signed=link, compact_json=compact_json)

  signature = None
  if signing_key:
    LOG.info("Signing link metadata using passed key...")
    signature = link_metadata.sign(signing_key)

  elif gpg_keyid:
    LOG.info("Signing link metadata using passed GPG keyid...")
    signature = link_metadata.sign_gpg(gpg_keyid, gpg_home=gpg_home)

  elif gpg_use_default:
    LOG.info("Signing link metadata using default GPG key ...")
    signature = link_metadata.sign_gpg(gpg_keyid=None, gpg_home=gpg_home)

  # We need the signature's keyid to write the link to keyid infix'ed filename
  if signature:
    signing_keyid = signature["keyid"]
    filename = FILENAME_FORMAT.format(step_name=name, keyid=signing_keyid)
    LOG.info("Storing link metadata to '{}'...".format(filename))
    link_metadata.dump(filename)

  return link_metadata