  def _HashDataStream(self, file_entry, data_stream_name=u''):
    """Hashes the contents of a specific data stream of a file entry.

    The resulting digest hashes are set in the parser mediator as attributes
    that are added to produced event objects. Note that some file systems
    allow directories to have data streams, e.g. NTFS.

    Args:
      file_entry: the file entry relating to the data to be hashed (instance of
                  dfvfs.FileEntry)
      data_stream_name: optional data stream name. The default is
                        an empty string which represents the default
                        data stream.
    """
    if not self._hasher_names:
      return

    logging.debug(u'[HashDataStream] hashing file: {0:s}'.format(
        self._current_display_name))

    file_object = file_entry.GetFileObject(data_stream_name=data_stream_name)
    if not file_object:
      return

    # Make sure frame.f_locals does not keep a reference to file_entry.
    file_entry = None

    try:
      digest_hashes = hashers_manager.HashersManager.HashFileObject(
          self._hasher_names, file_object,
          buffer_size=self._DEFAULT_HASH_READ_SIZE)
    finally:
      file_object.close()

    if self._enable_profiling:
      self._ProfilingSampleMemory()

    for hash_name, digest_hash_string in iter(digest_hashes.items()):
      attribute_name = u'{0:s}_hash'.format(hash_name)
      self._parser_mediator.AddEventAttribute(
          attribute_name, digest_hash_string)

      logging.debug(
          u'[HashDataStream] digest {0:s} calculated for file: {1:s}.'.format(
              digest_hash_string, self._current_display_name))

    logging.debug(
        u'[HashDataStream] completed hashing file: {0:s}'.format(
            self._current_display_name))