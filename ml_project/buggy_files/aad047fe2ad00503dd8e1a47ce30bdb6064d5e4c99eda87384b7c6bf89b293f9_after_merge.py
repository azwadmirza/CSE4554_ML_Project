def _enabled_used_error(ret):
    ret['result'] = False
    ret['comment'] = (
        'Service {0} uses non-existent option "enabled".  ' +
        'Perhaps "enable" option was intended?'
    ).format(ret['name'])
    return ret