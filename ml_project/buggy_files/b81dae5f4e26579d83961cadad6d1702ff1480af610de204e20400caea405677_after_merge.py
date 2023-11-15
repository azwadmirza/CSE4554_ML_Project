  def _ProcessDataStream(self, file_entry, data_stream_name=u''):
    """Processes a specific data stream of a file entry.

    Args:
      file_entry: A file entry object (instance of dfvfs.FileEntry).
      data_stream_name: optional data stream name. The default is
                        an empty string which represents the default
                        data stream.
    """
    file_object = file_entry.GetFileObject(data_stream_name=data_stream_name)
    if not file_object:
      return

    try:
      parser_name_list = self._GetSignatureMatchParserNames(file_object)
      if not parser_name_list:
        parser_name_list = self._non_sigscan_parser_names

      self._status = definitions.PROCESSING_STATUS_PARSING
      for parser_name in parser_name_list:
        parser_object = self._parser_objects.get(parser_name, None)
        if not parser_object:
          logging.warning(u'No such parser: {0:s}'.format(parser_name))
          continue

        if parser_object.FILTERS:
          if not self._CanProcessFileEntryWithParser(file_entry, parser_object):
            continue

        logging.debug((
            u'[ProcessDataStream] parsing file: {0:s} with parser: '
            u'{1:s}').format(self._current_display_name, parser_name))

        self._ParseFileEntryWithParser(
            parser_object, file_entry, file_object=file_object)

    finally:
      file_object.close()

      # Make sure frame.f_locals does not keep a reference to file_entry.
      file_entry = None