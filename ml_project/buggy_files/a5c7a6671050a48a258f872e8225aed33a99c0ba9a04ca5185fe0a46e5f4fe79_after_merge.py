  def Parse(self, parser_context, file_entry, parser_chain=None):
    """Extract data from an OXML file.

    Args:
      parser_context: A parser context object (instance of ParserContext).
      file_entry: A file entry object (instance of dfvfs.FileEntry).
      parser_chain: Optional string containing the parsing chain up to this
                    point. The default is None.
    """
    file_object = file_entry.GetFileObject()

    if not zipfile.is_zipfile(file_object):
      raise errors.UnableToParseFile(
          u'[{0:s}] unable to parse file: {1:s} with error: {2:s}'.format(
              self.NAME, file_entry.name, 'Not a Zip file.'))

    try:
      zip_container = zipfile.ZipFile(file_object, 'r')
    except (zipfile.BadZipfile, struct.error, zipfile.LargeZipFile):
      raise errors.UnableToParseFile(
          u'[{0:s}] unable to parse file: {1:s} with error: {2:s}'.format(
              self.NAME, file_entry.name, 'Bad Zip file.'))

    zip_name_list = set(zip_container.namelist())

    if not self._FILES_REQUIRED.issubset(zip_name_list):
      raise errors.UnableToParseFile(
          u'[{0:s}] unable to parse file: {1:s} with error: {2:s}'.format(
              self.NAME, file_entry.name, 'OXML element(s) missing.'))

    # Add ourselves to the parser chain, which will be used in all subsequent
    # event creation in this parser.
    parser_chain = self._BuildParserChain(parser_chain)

    metadata = {}
    timestamps = {}

    try:
      rels_xml = zip_container.read('_rels/.rels')
    except zipfile.BadZipfile as exception:
      logging.error(
          u'Unable to parse file {0:s} with error: {1:s}'.format(
              file_entry.name, exception))
      return

    rels_root = ElementTree.fromstring(rels_xml)

    for properties in rels_root.iter():
      if 'properties' in repr(properties.get('Type')):
        try:
          xml = zip_container.read(properties.get('Target'))
          root = ElementTree.fromstring(xml)
        except (
            OverflowError, IndexError, KeyError, ValueError,
            zipfile.BadZipfile) as exception:
          logging.warning(
              u'[{0:s}] unable to read property with error: {1:s}.'.format(
                  self.NAME, exception))
          continue

        for element in root.iter():
          if element.text:
            _, _, tag = element.tag.partition('}')
            # Not including the 'lpstr' attribute because it is
            # very verbose.
            if tag == 'lpstr':
              continue

            if tag in ('created', 'modified', 'lastPrinted'):
              timestamps[tag] = element.text
            else:
              tag_name = self._METAKEY_TRANSLATE.get(tag, self._FixString(tag))
              metadata[tag_name] = element.text

    if timestamps.get('created', None):
      event_object = OpenXMLParserEvent(
          timestamps.get('created'), eventdata.EventTimestamp.CREATION_TIME,
          metadata)
      parser_context.ProduceEvent(
          event_object, parser_chain=parser_chain, file_entry=file_entry)

    if timestamps.get('modified', None):
      event_object = OpenXMLParserEvent(
          timestamps.get('modified'),
          eventdata.EventTimestamp.MODIFICATION_TIME, metadata)
      parser_context.ProduceEvent(
          event_object, parser_chain=parser_chain, file_entry=file_entry)

    if timestamps.get('lastPrinted', None):
      event_object = OpenXMLParserEvent(
          timestamps.get('lastPrinted'), eventdata.EventTimestamp.LAST_PRINTED,
          metadata)
      parser_context.ProduceEvent(
          event_object, parser_chain=parser_chain, file_entry=file_entry)