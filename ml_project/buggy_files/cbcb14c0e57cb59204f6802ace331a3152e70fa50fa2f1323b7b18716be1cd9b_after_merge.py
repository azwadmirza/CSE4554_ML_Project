  def Parse(self, parser_context, file_entry, parser_chain=None):
    """Extract event objects from Chrome Cache files.

    Args:
      parser_context: A parser context object (instance of ParserContext).
      file_entry: A file entry object (instance of dfvfs.FileEntry).
      parser_chain: Optional string containing the parsing chain up to this
                    point. The default is None.
    """
    file_object = file_entry.GetFileObject()
    index_file = IndexFile()
    try:
      index_file.Open(file_object)
    except IOError as exception:
      file_object.close()
      raise errors.UnableToParseFile(
          u'[{0:s}] unable to parse index file {1:s} with error: {2:s}'.format(
              self.NAME, file_entry.name, exception))

    # Build a lookup table for the data block files.
    file_system = file_entry.GetFileSystem()
    path_segments = file_system.SplitPath(file_entry.path_spec.location)

    # Add ourselves to the parser chain, which will be used in all subsequent
    # event creation in this parser.
    parser_chain = self._BuildParserChain(parser_chain)

    data_block_files = {}
    for cache_address in index_file.index_table:
      if cache_address.filename not in data_block_files:
        # Remove the previous filename from the path segments list and
        # add one of the data block file.
        path_segments.pop()
        path_segments.append(cache_address.filename)

        # We need to pass only used arguments to the path specification
        # factory otherwise it will raise.
        kwargs = {}
        if file_entry.path_spec.parent:
          kwargs['parent'] = file_entry.path_spec.parent
        kwargs['location'] = file_system.JoinPath(path_segments)

        data_block_file_path_spec = path_spec_factory.Factory.NewPathSpec(
            file_entry.path_spec.TYPE_INDICATOR, **kwargs)

        try:
          data_block_file_entry = path_spec_resolver.Resolver.OpenFileEntry(
              data_block_file_path_spec)
        except RuntimeError as exception:
          logging.error((
              u'[{0:s}] Unable to open data block file: {1:s} while parsing '
              u'{2:s} with error: {3:s}').format(
                  parser_chain, kwargs['location'],
                  file_entry.path_spec.comparable, exception))
          data_block_file_entry = None

        if not data_block_file_entry:
          logging.error(u'Missing data block file: {0:s}'.format(
              cache_address.filename))
          data_block_file = None

        else:
          data_block_file_object = data_block_file_entry.GetFileObject()
          data_block_file = DataBlockFile()

          try:
            data_block_file.Open(data_block_file_object)
          except IOError as exception:
            logging.error((
                u'Unable to open data block file: {0:s} with error: '
                u'{1:s}').format(cache_address.filename, exception))
            data_block_file = None

        data_block_files[cache_address.filename] = data_block_file

    # Parse the cache entries in the data block files.
    for cache_address in index_file.index_table:
      cache_address_chain_length = 0
      while cache_address.value != 0x00000000:
        if cache_address_chain_length >= 64:
          logging.error(u'Maximum allowed cache address chain length reached.')
          break

        data_file = data_block_files.get(cache_address.filename, None)
        if not data_file:
          logging.debug(u'Cache address: 0x{0:08x} missing data file.'.format(
              cache_address.value))
          break

        try:
          cache_entry = data_file.ReadCacheEntry(cache_address.block_offset)
        except IOError as exception:
          logging.error(
              u'Unable to parse cache entry with error: {0:s}'.format(
                  exception))
          break

        event_object = ChromeCacheEntryEvent(cache_entry)
        parser_context.ProduceEvent(
            event_object, parser_chain=parser_chain, file_entry=file_entry)

        cache_address = cache_entry.next
        cache_address_chain_length += 1

    for data_block_file in data_block_files.itervalues():
      if data_block_file:
        data_block_file.Close()

    index_file.Close()