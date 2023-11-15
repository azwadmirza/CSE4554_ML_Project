  def AddArguments(cls, argument_group):
    """Adds command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group (argparse._ArgumentGroup|argparse.ArgumentParser): group
          to append arguments to.
    """
    argument_group.add_argument(
        '--nsrlsvr-hash', '--nsrlsvr_hash', dest='nsrlsvr_hash', type=str,
        action='store', choices=nsrlsvr.NsrlsvrAnalyzer.SUPPORTED_HASHES,
        default=cls._DEFAULT_HASH, metavar='HASH', help=(
            'Type of hash to use to query nsrlsvr instance, the default is: '
            '{0:s}. Supported options: {1:s}'.format(
                cls._DEFAULT_HASH, ', '.join(
                    nsrlsvr.NsrlsvrAnalyzer.SUPPORTED_HASHES))))

    argument_group.add_argument(
        '--nsrlsvr-host', '--nsrlsvr_host', dest='nsrlsvr_host', type=str,
        action='store', default=cls._DEFAULT_HOST, metavar='HOST',
        help=(
            'Hostname or IP address of the nsrlsvr instance to query, the '
            'default is: {0:s}').format(cls._DEFAULT_HOST))

    argument_group.add_argument(
        '--nsrlsvr-label', '--nsrlsvr_label', dest='nsrlsvr_label', type=str,
        action='store', default=cls._DEFAULT_LABEL, metavar='LABEL', help=(
            'Label to apply to events, the default is: '
            '{0:s}.').format(cls._DEFAULT_LABEL))

    argument_group.add_argument(
        '--nsrlsvr-port', '--nsrlsvr_port', dest='nsrlsvr_port', type=int,
        action='store', default=cls._DEFAULT_PORT, metavar='PORT', help=(
            'Port number of the nsrlsvr instance to query, the default is: '
            '{0:d}.').format(cls._DEFAULT_PORT))