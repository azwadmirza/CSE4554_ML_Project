  def ParseFileObject(
      self, parser_context, file_object, file_entry=None, parser_chain=None):
    """Extract data from an *.customDestinations-ms file.

    Args:
      parser_context: A parser context object (instance of ParserContext).
      file_object: A file-like object.
      file_entry: Optional file entry object (instance of dfvfs.FileEntry).
                  The default is None.
      parser_chain: Optional string containing the parsing chain up to this
                    point. The default is None.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    parser_chain = self._BuildParserChain(parser_chain)

    try:
      file_header = self._FILE_HEADER.parse_stream(file_object)
    except (IOError, construct.FieldError) as exception:
      raise errors.UnableToParseFile((
          u'Unable to parse Custom Destination file header with error: '
          u'{0:s}').format(exception))

    if file_header.unknown1 != 2:
      raise errors.UnableToParseFile((
          u'Unsupported Custom Destination file - invalid unknown1: '
          u'{0:d}.').format(file_header.unknown1))

    if file_header.header_values_type > 2:
      raise errors.UnableToParseFile((
          u'Unsupported Custom Destination file - invalid header value type: '
          u'{0:d}.').format(file_header.header_values_type))

    if file_header.header_values_type == 0:
      data_structure = self._HEADER_VALUE_TYPE_0
    else:
      data_structure = self._HEADER_VALUE_TYPE_1_OR_2

    try:
      _ = data_structure.parse_stream(file_object)
    except (IOError, construct.FieldError) as exception:
      raise errors.UnableToParseFile((
          u'Unable to parse Custom Destination file header value with error: '
          u'{0:s}').format(exception))

    file_size = file_object.get_size()
    file_offset = file_object.get_offset()
    remaining_file_size = file_size - file_offset

    # The Custom Destination file does not have a unique signature in
    # the file header that is why we use the first LNK class identifier (GUID)
    # as a signature.
    first_guid_checked = False
    while remaining_file_size > 4:
      try:
        entry_header = self._ENTRY_HEADER.parse_stream(file_object)
      except (IOError, construct.FieldError) as exception:
        if not first_guid_checked:
          raise errors.UnableToParseFile((
              u'Unable to parse Custom Destination file entry header with '
              u'error: {0:s}').format(exception))
        else:
          logging.warning((
              u'Unable to parse Custom Destination file entry header with '
              u'error: {0:s}').format(exception))
        break

      if entry_header.guid != self._LNK_GUID:
        if not first_guid_checked:
          raise errors.UnableToParseFile(
              u'Unsupported Custom Destination file - invalid entry header.')
        else:
          logging.warning(
              u'Unsupported Custom Destination file - invalid entry header.')
        break

      first_guid_checked = True
      file_offset += 16
      remaining_file_size -= 16

      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_DATA_RANGE, range_offset=file_offset,
          range_size=remaining_file_size, parent=file_entry.path_spec)

      try:
        lnk_file_object = resolver.Resolver.OpenFileObject(path_spec)
      except RuntimeError as exception:
        logging.error((
            u'[{0:s}] Unable to open LNK file from {1:s} with error: '
            u'{2:s}').format(
                parser_chain,
                file_entry.path_spec.comparable.replace(u'\n', u';'),
                exception))
        return

      display_name = u'{0:s} # 0x{1:08x}'.format(
          parser_context.GetDisplayName(file_entry), file_offset)

      self._WINLNK_PARSER.ParseFileObject(
          parser_context, lnk_file_object, file_entry=file_entry,
          parser_chain=parser_chain, display_name=display_name)

      # We cannot trust the file size in the LNK data so we get the last offset
      # that was read instead.
      lnk_file_size = lnk_file_object.get_offset()

      lnk_file_object.close()

      file_offset += lnk_file_size
      remaining_file_size -= lnk_file_size

      file_object.seek(file_offset, os.SEEK_SET)

    try:
      file_footer = self._FILE_FOOTER.parse_stream(file_object)
    except (IOError, construct.FieldError) as exception:
      logging.warning((
          u'Unable to parse Custom Destination file footer with error: '
          u'{0:s}').format(exception))

    if file_footer.signature != 0xbabffbab:
      logging.warning(
          u'Unsupported Custom Destination file - invalid footer signature.')