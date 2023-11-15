  def AddArguments(cls, argument_group):
    """Adds command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group (argparse._ArgumentGroup|argparse.ArgumentParser): group
          to append arguments to.
    """
    argument_group.add_argument(
        u'--nsrlsvr-host', dest=u'nsrlsvr_host', type=str, action='store',
        default=cls._DEFAULT_HOST,
        help=u'Specify the host to query Nsrlsvr on.')
    argument_group.add_argument(
        u'--nsrlsvr-port', dest=u'nsrlvr_port', type=int, action='store',
        default=cls._DEFAULT_PORT,
        help=u'Port to use to query Nsrlsvr.')