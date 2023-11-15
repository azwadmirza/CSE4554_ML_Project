def register_instances(name, instances, region=None, key=None, keyid=None,
                       profile=None):
    '''
    Add EC2 instance(s) to an Elastic Load Balancer. Removing an instance from
    the ``instances`` list does not remove it from the ELB.

    name
        The name of the Elastic Load Balancer to add EC2 instances to.

    instances
        A list of EC2 instance IDs that this Elastic Load Balancer should
        distribute traffic to. This state will only ever append new instances
        to the ELB. EC2 instances already associated with this ELB will not be
        removed if they are not in the ``instances`` list.

    .. versionadded:: 2015.8.0

    .. code-block:: yaml

        add-instances:
          boto_elb.register_instances:
            - name: myloadbalancer
            - instances:
              - instance-id1
              - instance-id2
    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}
    lb = __salt__['boto_elb.exists'](name, region, key, keyid, profile)
    if lb:
        health = __salt__['boto_elb.get_instance_health'](name,
                                                          region,
                                                          key,
                                                          keyid,
                                                          profile)
        nodes = []
        new = []
        for value in health:
            nodes.append(value['instance_id'])
        for value in instances:
            if value not in nodes:
                new.append(value)
        if len(new) == 0:
            ret['comment'] = 'Instance/s {0} already exist.' \
                              ''.format(str(instances).strip('[]'))
            ret['result'] = True
        else:
            if __opts__['test']:
                ret['comment'] = 'ELB {0} is set to register : {1}.'.format(name, new)
                ret['result'] = None
                return ret
            state = __salt__['boto_elb.register_instances'](name,
                                                            instances,
                                                            region,
                                                            key,
                                                            keyid,
                                                            profile)
            if state:
                ret['comment'] = 'Load Balancer {0} has been changed' \
                                 ''.format(name)
                ret['changes']['old'] = '\n'.join(nodes)
                new = set().union(nodes, instances)
                ret['changes']['new'] = '\n'.join(list(new))
                ret['result'] = True
            else:
                ret['comment'] = 'Load balancer {0} failed to add instances' \
                                 ''.format(name)
                ret['result'] = False
    else:
        ret['comment'] = 'Could not find lb {0}'.format(name)
    return ret