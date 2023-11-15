  def ParseFileTransfer(
      self, parser_mediator, row, cache=None, database=None, query=None,
      **unused_kwargs):
    """Parse the transfer files.

     There is no direct relationship between who sends the file and
     who accepts the file.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      row: the row with all information related with the file transfers.
      query: Optional query string.
      cache: a cache object (instance of SQLiteCache).
      database: A database object (instance of SQLiteDatabase).
    """
    # Note that pysqlite does not accept a Unicode string in row['string'] and
    # will raise "IndexError: Index must be int or string".

    source_dict = cache.GetResults(u'source')
    if not source_dict:
      results = database.Query(self.QUERY_SOURCE_FROM_TRANSFER)

      # Note that pysqlite does not accept a Unicode string in row['string'] and
      # will raise "IndexError: Index must be int or string".
      cache.CacheQueryResults(
          results, 'source', 'pk_id', ('skypeid', 'skypename'))
      source_dict = cache.GetResults(u'source')

    dest_dict = cache.GetResults(u'destination')
    if not dest_dict:
      results = database.Query(self.QUERY_DEST_FROM_TRANSFER)

      # Note that pysqlite does not accept a Unicode string in row['string'] and
      # will raise "IndexError: Index must be int or string".
      cache.CacheQueryResults(
          results, 'destination', 'parent_id', ('skypeid', 'skypename'))
      dest_dict = cache.GetResults(u'destination')

    source = u'Unknown'
    destination = u'Unknown'

    if row['parent_id']:
      destination = u'{0:s} <{1:s}>'.format(
          row['partner_handle'], row['partner_dispname'])
      skype_id, skype_name = source_dict.get(row['parent_id'], [None, None])
      if skype_name:
        source = u'{0:s} <{1:s}>'.format(skype_id, skype_name)
    else:
      source = u'{0:s} <{1:s}>'.format(
          row['partner_handle'], row['partner_dispname'])

      if row['pk_id']:
        skype_id, skype_name = dest_dict.get(row['pk_id'], [None, None])
        if skype_name:
          destination = u'{0:s} <{1:s}>'.format(skype_id, skype_name)

    try:
      # TODO: add a conversion base.
      file_size = int(row['filesize'])
    except ValueError:
      parser_mediator.ProduceParseError(
          u'unable to convert file size: {0!s} of file: {1:s}'.format(
              row['filesize'], row['filename']))
      file_size = 0

    if row['status'] == 8:
      if row['starttime']:
        event_object = SkypeTransferFileEvent(
            row['starttime'], row['id'], u'GETSOLICITUDE', source, destination,
            row['filename'], row['filepath'], file_size)
        parser_mediator.ProduceEvent(event_object, query=query)

      if row['accepttime']:
        event_object = SkypeTransferFileEvent(
            row['accepttime'], row['id'], u'ACCEPTED', source, destination,
            row['filename'], row['filepath'], file_size)
        parser_mediator.ProduceEvent(event_object, query=query)

      if row['finishtime']:
        event_object = SkypeTransferFileEvent(
            row['finishtime'], row['id'], u'FINISHED', source, destination,
            row['filename'], row['filepath'], file_size)
        parser_mediator.ProduceEvent(event_object, query=query)

    elif row['status'] == 2 and row['starttime']:
      event_object = SkypeTransferFileEvent(
          row['starttime'], row['id'], u'SENDSOLICITUDE', source, destination,
          row['filename'], row['filepath'], file_size)
      parser_mediator.ProduceEvent(event_object, query=query)