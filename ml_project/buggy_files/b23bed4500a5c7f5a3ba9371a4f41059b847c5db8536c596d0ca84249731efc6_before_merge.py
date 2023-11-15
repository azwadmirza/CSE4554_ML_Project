def volume_absent(name, driver=None):
    '''
    Ensure that a volume is absent.

    .. versionadded:: 2015.8.4

    name
        Name of the volume

    Usage Examples:

    .. code-block:: yaml

        volume_foo:
          dockerng.volume_absent

    '''
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    volumes = [v for v in __salt__['dockerng.volumes']()['Volumes'] if v['Name'] == name]
    if not volumes:
        ret['result'] = True
        ret['comment'] = 'Volume \'{0}\' already absent'.format(name)
        return ret

    try:
        ret['changes']['removed'] = __salt__['dockerng.remove_volume'](name)
        ret['result'] = True
    except Exception as exc:
        ret['comment'] = ('Failed to remove volume \'{0}\': {1}'
                          .format(name, exc))
    return ret