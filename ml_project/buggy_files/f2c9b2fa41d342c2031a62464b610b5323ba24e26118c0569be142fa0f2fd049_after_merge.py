def get_delegated_roles_metadata_filenames(metadata_directory,
    consistent_snapshot, storage_backend=None):
  """
  Return a dictionary containing all filenames in 'metadata_directory'
  except the top-level roles.
  If multiple versions of a file exist because of a consistent snapshot,
  only the file with biggest version prefix is included.
  """

  filenames = {}
  metadata_files = sorted(storage_backend.list_folder(metadata_directory),
      reverse=True)

  # Iterate over role metadata files, sorted by their version-number prefix, with
  # more recent versions first, and only add the most recent version of any
  # (non top-level) metadata to the list of returned filenames. Note that there
  # should only be one version of each file, if consistent_snapshot is False.
  for metadata_role in metadata_files:
    metadata_path = os.path.join(metadata_directory, metadata_role)

    # Strip the version number if 'consistent_snapshot' is True,
    # or if 'metadata_role' is Root.
    # Example:  '10.django.json' --> 'django.json'
    consistent = \
      metadata_role.endswith('root.json') or consistent_snapshot == True
    metadata_name, junk = _strip_version_number(metadata_role,
      consistent)

    if metadata_name.endswith(METADATA_EXTENSION):
      extension_length = len(METADATA_EXTENSION)
      metadata_name = metadata_name[:-extension_length]

    else:
      logger.debug('Skipping file with unsupported metadata'
          ' extension: ' + repr(metadata_path))
      continue

    # Skip top-level roles, only interested in delegated roles.
    if metadata_name in tuf.roledb.TOP_LEVEL_ROLES:
      continue

    # Prevent reloading duplicate versions if consistent_snapshot is True
    if metadata_name not in filenames:
      filenames[metadata_name] = metadata_path

  return filenames