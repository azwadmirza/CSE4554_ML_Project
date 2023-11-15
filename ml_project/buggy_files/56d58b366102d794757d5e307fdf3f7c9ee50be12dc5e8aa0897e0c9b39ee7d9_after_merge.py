  def AddArguments(cls, argument_group):
    """Adds command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group (argparse._ArgumentGroup|argparse.ArgumentParser):
          argparse group.
    """
    argument_group.add_argument(
        u'--viper-hash', u'--viper_hash', dest=u'viper_hash', type=str,
        action='store', choices=[u'sha256'], default=cls._DEFAULT_HASH,
        metavar=u'HASH', help=(
            u'Type of hash to use to query the Viper server, the default is: '
            u'{0:s}'.format(cls._DEFAULT_HASH)))

    argument_group.add_argument(
        u'--viper-host', u'--viper_host', dest=u'viper_host', type=str,
        action='store', default=cls._DEFAULT_HOST, metavar=u'HOST',
        help=(
            u'Hostname of the Viper server to query, the default is: '
            u'{0:s}'.format(cls._DEFAULT_HOST)))

    argument_group.add_argument(
        u'--viper-port', u'--viper_port', dest=u'viper_port', type=int,
        action='store', default=cls._DEFAULT_PORT, metavar=u'PORT', help=(
            u'Port of the Viper server to query, the default is: {0:d}.'.format(
                cls._DEFAULT_PORT)))

    argument_group.add_argument(
        u'--viper-protocol', u'--viper_protocol', dest=u'viper_protocol',
        type=str, choices=[u'http', u'https'], action='store',
        default=cls._DEFAULT_PROTOCOL, metavar=u'PROTOCOL', help=(
            u'Protocol to use to query Viper.'))