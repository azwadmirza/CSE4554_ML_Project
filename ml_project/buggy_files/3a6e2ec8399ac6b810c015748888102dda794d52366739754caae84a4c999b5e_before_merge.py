def cli(name, format='text', **kwargs):
    '''
    Executes the CLI commands and reuturns the text output.

    .. code-block:: yaml

            show version:
              junos:
                - cli
                - format: xml

    Parameters:
      Required
        * command:
          The command that need to be executed on Junos CLI. (default = None)
      Optional
        * format:
          Format in which to get the CLI output. (text or xml, \
            default = 'text')
        * kwargs: Keyworded arguments which can be provided like-
            * timeout:
              Set NETCONF RPC timeout. Can be used for commands which
              take a while to execute. (default = 30 seconds)
            * dest:
              The destination file where the CLI output can be stored.\
               (default = None)
    '''
    ret = {'name': name, 'changes': {}, 'result': True, 'comment': ''}
    ret['changes'] = __salt__['junos.cli'](name, format, **kwargs)
    return ret