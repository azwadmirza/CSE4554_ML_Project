  def AddArguments(cls, argument_group):
    """Adds command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group (argparse._ArgumentGroup|argparse.ArgumentParser):
          argparse group.
    """
    argument_group.add_argument(
        u'--virustotal-api-key', u'--virustotal_api_key',
        dest=u'virustotal_api_key', type=str, action='store', default=None,
        metavar=u'API_KEY', help=(
            u'Specify the API key for use with VirusTotal.'))

    argument_group.add_argument(
        u'--virustotal-free-rate-limit', u'--virustotal_free_rate_limit',
        dest=u'virustotal_free_rate_limit',
        action='store_false', default=cls._DEFAULT_RATE_LIMIT, help=(
            u'Limit Virustotal requests to the default free API key rate of '
            u'4 requests per minute. Set this to false if you have an key '
            u'for the private API.'))

    argument_group.add_argument(
        u'--virustotal-hash', u'--virustotal_hash', dest=u'virustotal_hash',
        type=str, action='store', choices=[u'md5', u'sha1', u'sha256'],
        default=cls._DEFAULT_HASH, metavar=u'HASH', help=(
            u'Type of hash to query VirusTotal, the default is: {0:s}'.format(
                cls._DEFAULT_HASH)))