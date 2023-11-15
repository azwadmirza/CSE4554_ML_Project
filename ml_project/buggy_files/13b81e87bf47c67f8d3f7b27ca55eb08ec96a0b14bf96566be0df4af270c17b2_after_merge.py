  def _PreprocessSource(self, source_path_specs):
    """Preprocesses the source.

    Args:
      source_path_specs: list of path specifications (instances of
                         dfvfs.PathSpec) to process.

    Returns:
      The preprocessing object (instance of PreprocessObject).
    """
    pre_obj = None

    if self._old_preprocess and os.path.isfile(self._storage_file_path):
      # Check if the storage file contains a preprocessing object.
      try:
        with storage.StorageFile(
            self._storage_file_path, read_only=True) as store:
          storage_information = store.GetStorageInformation()
          if storage_information:
            logging.info(u'Using preprocessing information from a prior run.')
            pre_obj = storage_information[-1]
            self._preprocess = False
      except IOError:
        logging.warning(u'Storage file does not exist, running preprocess.')

    logging.debug(u'Starting preprocessing.')

    if (self._preprocess and
        (self.SourceIsDirectory() or self.SourceIsStorageMediaImage())):
      try:
        self._engine.PreprocessSource(
            source_path_specs, self._operating_system,
            resolver_context=self._resolver_context)

      except IOError as exception:
        logging.error(u'Unable to preprocess with error: {0:s}'.format(
            exception))
        return event.PreprocessObject()

    logging.debug(u'Preprocessing done.')

    # TODO: Remove the need for direct access to the pre_obj in favor
    # of the knowledge base.
    pre_obj = getattr(self._engine.knowledge_base, u'_pre_obj', None)

    if not pre_obj:
      pre_obj = event.PreprocessObject()

    return pre_obj