def __virtual__():
    return 'elasticsearch.alias_exists' in __salt__