def cli(name, **kwargs):
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
        * kwargs: Keyworded arguments which can be provided like-
            * format:
              Format in which to get the CLI output. (text or xml, \
                default = 'text')
            * timeout:
              Set NETCONF RPC timeout. Can be used for commands which
              take a while to execute. (default = 30 seconds)
            * dest:
              The destination file where the CLI output can be stored.\
               (default = None)
    '''
    ret = {'name': name, 'changes': {}, 'result': True, 'comment': ''}
    ret['changes'] = __salt__['junos.cli'](name, **kwargs)
    return ret