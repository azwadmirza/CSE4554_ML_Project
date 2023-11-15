  def ParseArguments(self):
    """Parses the command line arguments.

    Returns:
      A boolean value indicating the arguments were successfully parsed.
    """
    logging.basicConfig(
        level=logging.INFO, format=u'[%(levelname)s] %(message)s')

    argument_parser = argparse.ArgumentParser(
        description=self.DESCRIPTION, epilog=self.EPILOG, add_help=False)

    self.AddBasicOptions(argument_parser)
    self.AddInformationalOptions(argument_parser)
    self.AddDataLocationOption(argument_parser)

    argument_parser.add_argument(
        u'-w', u'--write', action=u'store', dest=u'path', type=unicode,
        metavar=u'PATH', default=u'export', help=(
            u'The directory in which extracted files should be stored.'))

    argument_parser.add_argument(
        u'-f', u'--filter', action=u'store', dest=u'filter', type=unicode,
        metavar=u'FILTER_FILE', help=(
            u'Full path to the file that contains the collection filter, '
            u'the file can use variables that are defined in preprocessing, '
            u'just like any other log2timeline/plaso collection filter.'))

    argument_parser.add_argument(
        u'--date-filter', u'--date_filter', action=u'append', type=unicode,
        dest=u'date_filters', metavar=u'TYPE_START_END', default=None, help=(
            u'Filter based on file entry date and time ranges. This parameter '
            u'is formatted as "TIME_VALUE,START_DATE_TIME,END_DATE_TIME" where '
            u'TIME_VALUE defines which file entry timestamp the filter applies '
            u'to e.g. atime, ctime, crtime, bkup, etc. START_DATE_TIME and '
            u'END_DATE_TIME define respectively the start and end of the date '
            u'time range. A date time range requires at minimum start or end '
            u'to time of the boundary and END defines the end time. Both '
            u'timestamps be set. The date time values are formatted as: '
            u'YYYY-MM-DD hh:mm:ss.######[+-]##:## Where # are numeric digits '
            u'ranging from 0 to 9 and the seconds fraction can be either 3 '
            u'or 6 digits. The time of day, seconds fraction and timezone '
            u'offset are optional. The default timezone is UTC. E.g. "atime, '
            u'2013-01-01 23:12:14, 2013-02-23". This parameter can be repeated '
            u'as needed to add additional date date boundaries, eg: once for '
            u'atime, once for crtime, etc.'))

    argument_parser.add_argument(
        u'-x', u'--extensions', dest=u'extensions_string', action=u'store',
        type=unicode, metavar=u'EXTENSIONS', help=(
            u'Filter based on file name extensions. This option accepts '
            u'multiple multiple comma separated values e.g. "csv,docx,pst".'))

    argument_parser.add_argument(
        u'--names', dest=u'names_string', action=u'store',
        type=str, metavar=u'NAMES', help=(
            u'If the purpose is to find all files given a certain names '
            u'this options should be used. This option accepts a comma '
            u'separated string denoting all file names, eg: -x '
            u'"NTUSER.DAT,UsrClass.dat".'))

    argument_parser.add_argument(
        u'--signatures', dest=u'signature_identifiers', action=u'store',
        type=unicode, metavar=u'IDENTIFIERS', help=(
            u'Filter based on file format signature identifiers. This option '
            u'accepts multiple comma separated values e.g. "esedb,lnk". '
            u'Use "list" to show an overview of the supported file format '
            u'signatures.'))

    argument_parser.add_argument(
        u'--include_duplicates', dest=u'include_duplicates',
        action=u'store_true', default=False, help=(
            u'If extraction from VSS is enabled, by default a digest hash '
            u'is calcuted for each file. These hases are compared to the '
            u'previously exported files and duplicates are skipped. Use '
            u'this option to include duplicate files in the export.'))

    self.AddStorageMediaImageOptions(argument_parser)
    self.AddVssProcessingOptions(argument_parser)

    argument_parser.add_argument(
        u'image', nargs='?', action=u'store', metavar=u'IMAGE', default=None,
        type=unicode, help=(
            u'The full path to the image file that we are about to extract '
            u'files from, it should be a raw image or another image that '
            u'plaso supports.'))

    try:
      options = argument_parser.parse_args()
    except UnicodeEncodeError:
      # If we get here we are attempting to print help in a non-Unicode
      # terminal.
      self._output_writer.Write(u'')
      self._output_writer.Write(argument_parser.format_help())
      return False

    try:
      self.ParseOptions(options)
    except errors.BadConfigOption as exception:
      logging.error(u'{0:s}'.format(exception))

      self._output_writer.Write(u'')
      self._output_writer.Write(argument_parser.format_help())

      return False

    return True