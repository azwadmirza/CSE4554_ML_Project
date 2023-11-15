def list_present(name, value, delimiter=DEFAULT_TARGET_DELIM):
    '''
    .. versionadded:: 2014.1.0

    Ensure the value is present in the list-type grain. Note: If the grain that is
    provided in ``name`` is not present on the system, this new grain will be created
    with the corresponding provided value.

    name
        The grain name.

    value
        The value is present in the list type grain.

    delimiter
        A delimiter different from the default ``:`` can be provided.

        .. versionadded:: v2015.8.2

    The grain should be `list type <http://docs.python.org/2/tutorial/datastructures.html#data-structures>`_

    .. code-block:: yaml

        roles:
          grains.list_present:
            - value: web

    For multiple grains, the syntax looks like:

    .. code-block:: yaml

        roles:
          grains.list_present:
            - value:
              - web
              - dev
    '''
    name = re.sub(delimiter, DEFAULT_TARGET_DELIM, name)
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    grain = __salt__['grains.get'](name)
    if grain:
        # check whether grain is a list
        if not isinstance(grain, list):
            ret['result'] = False
            ret['comment'] = 'Grain {0} is not a valid list'.format(name)
            return ret
        if isinstance(value, list):
            if set(value).issubset(set(__salt__['grains.get'](name))):
                ret['comment'] = 'Value {1} is already in grain {0}'.format(name, value)
                return ret
            elif name in __context__.get('pending_grains', {}):
                # elements common to both
                intersection = set(value).intersection(__context__.get('pending_grains', {})[name])
                if intersection:
                    value = list(set(value).difference(__context__['pending_grains'][name]))
                    ret['comment'] = 'Removed value {0} from update due to context found in "{1}".\n'.format(value, name)
            if 'pending_grains' not in __context__:
                __context__['pending_grains'] = {}
            if name not in __context__['pending_grains']:
                __context__['pending_grains'][name] = set()
            __context__['pending_grains'][name].update(value)
        else:
            if value in grain:
                ret['comment'] = 'Value {1} is already in grain {0}'.format(name, value)
                return ret
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'Value {1} is set to be appended to grain {0}'.format(name, value)
            ret['changes'] = {'new': grain}
            return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Grain {0} is set to be added'.format(name)
        ret['changes'] = {'new': grain}
        return ret
    new_grains = __salt__['grains.append'](name, value)
    if isinstance(value, list):
        if not set(value).issubset(set(__salt__['grains.get'](name))):
            ret['result'] = False
            ret['comment'] = 'Failed append value {1} to grain {0}'.format(name, value)
            return ret
    else:
        if value not in __salt__['grains.get'](name, delimiter=DEFAULT_TARGET_DELIM):
            ret['result'] = False
            ret['comment'] = 'Failed append value {1} to grain {0}'.format(name, value)
            return ret
    ret['comment'] = 'Append value {1} to grain {0}'.format(name, value)
    ret['changes'] = {'new': new_grains}
    return ret