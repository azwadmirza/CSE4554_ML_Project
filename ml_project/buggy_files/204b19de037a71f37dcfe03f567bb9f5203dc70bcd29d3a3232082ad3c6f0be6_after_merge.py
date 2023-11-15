  def AddArguments(cls, argument_group):
    """Adds command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group (argparse._ArgumentGroup|argparse.ArgumentParser): group
          to append arguments to.
    """
    argument_group.add_argument(
        u'--nsrlsvr-hash', u'--nsrlsvr_hash', dest=u'nsrlsvr_hash', type=str,
        action='store', choices=[u'md5', u'sha1'], default=cls._DEFAULT_HASH,
        metavar=u'HASH', help=(
            u'Type of hash to use to query nsrlsvr instance, the default is: '
            u'{0:s}').format(cls._DEFAULT_HASH))

    argument_group.add_argument(
        u'--nsrlsvr-host', u'--nsrlsvr_host', dest=u'nsrlsvr_host', type=str,
        action='store', default=cls._DEFAULT_HOST, metavar=u'HOST',
        help=(
            u'Hostname or IP address of the nsrlsvr instance to query, the '
            u'default is: {0:s}').format(cls._DEFAULT_HOST))

    argument_group.add_argument(
        u'--nsrlsvr-port', u'--nsrlsvr_port', dest=u'nsrlvr_port', type=int,
        action='store', default=cls._DEFAULT_PORT, metavar=u'PORT', help=(
            u'Port number of the nsrlsvr instance to query, the default is: '
            u'{0:d}.').format(cls._DEFAULT_PORT))