  def AddArguments(cls, argument_group):
    """Add command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group: the argparse group (instance of argparse._ArgumentGroup or
                      or argparse.ArgumentParser).
    """
    argument_group.add_argument(
        u'--fields', dest=u'fields', type=str, action=u'store',
        nargs=u'*', default=u','.join(cls._DEFAULT_FIELDS),
        help=u'Defines which fields should be included in the output.')
    argument_group.add_argument(
        u'--timestamp_format', dest=u'timestamp_format', type=str,
        action=u'store', default=cls._DEFAULT_TIMESTAMP_FORMAT, help=(
            u'Set the timestamp format that will be used in the datetime'
            u'column of the XLSX spreadsheet.'))