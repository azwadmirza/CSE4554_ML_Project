  def AddArguments(cls, argument_group):
    """Add command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group: the argparse group (instance of argparse._ArgumentGroup or
                      or argparse.ArgumentParser).
    """
    argument_group.add_argument(
        u'--append', dest=u'append', action=u'store_true', default=False,
        required=cls._DEFAULT_APPEND, help=(
            u'Defines whether the intention is to append to an already '
            u'existing database or overwrite it. Defaults to overwrite.'))
    argument_group.add_argument(
        u'--evidence', dest=u'evidence', type=str,
        default=cls._DEFAULT_EVIDENCE, action=u'store', required=False,
        help=u'Set the evidence field to a specific value, defaults to empty.')
    argument_group.add_argument(
        u'--fields', dest=u'fields', type=str, action=u'store',
        nargs=u'*', default=cls._DEFAULT_FIELDS,
        help=u'Defines which fields should be indexed in the database.')