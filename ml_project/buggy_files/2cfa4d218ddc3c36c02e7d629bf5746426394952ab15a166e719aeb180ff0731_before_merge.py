def coalesce(name, **kwargs):
    '''
    Manage coalescing settings of network device

    name
        Interface name to apply coalescing settings

    .. code-block:: yaml

        eth0:
          ethtool.coalesce:
            - name: eth0
            - adaptive_rx: on
            - adaptive_tx: on
            - rx_usecs: 24
            - rx_frame: 0
            - rx_usecs_irq: 0
            - rx_frames_irq: 0
            - tx_usecs: 48
            - tx_frames: 0
            - tx_usecs_irq: 0
            - tx_frames_irq: 0
            - stats_block_usecs: 0
            - pkt_rate_low: 0
            - rx_usecs_low: 0
            - rx_frames_low: 0
            - tx_usecs_low: 0
            - tx_frames_low: 0
            - pkt_rate_high: 0
            - rx_usecs_high: 0
            - rx_frames_high: 0
            - tx_usecs_high: 0
            - tx_frames_high: 0
            - sample_interval: 0

    '''
    ret = {
        'name': name,
        'changes': {},
        'result': True,
        'comment': 'Network device {0} coalescing settings are up to date.'.format(name),
    }
    apply_coalescing = False
    if 'test' not in kwargs:
        kwargs['test'] = __opts__.get('test', False)

    # Build coalescing settings
    try:
        old = __salt__['ethtool.show_coalesce'](name)
        if not isinstance(old, dict):
            ret['result'] = False
            ret['comment'] = 'Device {0} coalescing settings are not supported'.format(name)
            return ret

        new = {}
        diff = []

        # Retreive changes to made
        for key, value in kwargs.items():
            if key in ['adaptive_rx', 'adaptive_tx']:
                value = value and "on" or "off"
            if key in old and value != old[key]:
                new.update({key: value})
                diff.append('{0}: {1}'.format(key, value))

        # Dry run
        if kwargs['test']:
            if not new:
                return ret
            if new:
                ret['result'] = None
                ret['comment'] = 'Device {0} coalescing settings are set to be ' \
                                 'updated:\n{1}'.format(name, '\n'.join(diff))
                return ret

        # Prepare return output
        if new:
            apply_coalescing = True
            ret['comment'] = 'Device {0} coalescing settings updated.'.format(name)
            ret['changes']['ethtool_coalesce'] = '\n'.join(diff)

    except AttributeError as error:
        ret['result'] = False
        ret['comment'] = six.text_type(error)
        return ret

    # Apply coalescing settings
    if apply_coalescing:
        try:
            __salt__['ethtool.set_coalesce'](name, **new)
        except AttributeError as error:
            ret['result'] = False
            ret['comment'] = six.text_type(error)
            return ret

    return ret