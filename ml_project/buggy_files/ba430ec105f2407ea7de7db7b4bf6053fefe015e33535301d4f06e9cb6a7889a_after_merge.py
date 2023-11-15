def get_stack_events(cfn, stack_name, token_filter=None):
    '''This event data was never correct, it worked as a side effect. So the v2.3 format is different.'''
    ret = {'events':[], 'log':[]}

    try:
        pg = cfn.get_paginator(
            'describe_stack_events'
        ).paginate(
            StackName=stack_name
        )
        if token_filter is not None:
            events = list(pg.search(
                "StackEvents[?ClientRequestToken == '{0}']".format(token_filter)
            ))
        else:
            events = list(pg.search("StackEvents[*]"))
    except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as err:
        error_msg = boto_exception(err)
        if 'does not exist' in error_msg:
            # missing stack, don't bail.
            ret['log'].append('Stack does not exist.')
            return ret
        ret['log'].append('Unknown error: ' + str(error_msg))
        return ret

    for e in events:
        eventline = 'StackEvent {ResourceType} {LogicalResourceId} {ResourceStatus}'.format(**e)
        ret['events'].append(eventline)

        if e['ResourceStatus'].endswith('FAILED'):
            failline = '{ResourceType} {LogicalResourceId} {ResourceStatus}: {ResourceStatusReason}'.format(**e)
            ret['log'].append(failline)

    return ret