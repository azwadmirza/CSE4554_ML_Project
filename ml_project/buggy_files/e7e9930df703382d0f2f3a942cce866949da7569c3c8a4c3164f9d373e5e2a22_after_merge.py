  def Close(self):
    """Closes the storage, flush the last buffer and closes the ZIP file."""
    if not self._zipfile:
      return

    if not self._read_only and self._pre_obj:
      self._WritePreprocessObject(self._pre_obj)

    self._WriteBuffer()
    self._Close()

    if not self._read_only:
      logging.debug((
          u'[Storage] Closing the storage, number of events added: '
          u'{0:d}').format(self._write_counter))

    self._ProfilingStop()