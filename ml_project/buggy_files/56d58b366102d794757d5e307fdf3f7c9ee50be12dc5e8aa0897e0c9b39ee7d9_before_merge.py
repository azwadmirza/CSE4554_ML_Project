  def AddArguments(cls, argument_group):
    """Adds command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group (argparse._ArgumentGroup|argparse.ArgumentParser):
          argparse group.
    """
    argument_group.add_argument(
        u'--viper-host', dest=u'viper_host',
        type=str, action='store', default=cls._DEFAULT_HOST,
        help=u'Specify the host to query Viper on.')
    argument_group.add_argument(
        u'--viper-protocol', dest=u'viper_protocol', type=str,
        choices=[u'http', u'https'], action='store',
        default=cls._DEFAULT_PROTOCOL,
        help=u'Protocol to use to query Viper.')