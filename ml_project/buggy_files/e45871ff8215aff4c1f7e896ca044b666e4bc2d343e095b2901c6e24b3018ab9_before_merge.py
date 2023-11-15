def beacon(config):
    '''
    Emit the load averages of this host.

    Specify thresholds for each load average
    and only emit a beacon if any of them are
    exceeded.

    .. code-block:: yaml

        beacons:
          - load:
            - 1m:
              - 0.0
              - 2.0
            - 5m:
              - 0.0
              - 1.5
            - 15m:
              - 0.1
              - 1.0

    '''
    log.trace('load beacon starting')
    ret = []
    if not os.path.isfile('/proc/loadavg'):
        return ret
    with salt.utils.fopen('/proc/loadavg', 'rb') as fp_:
        avgs = fp_.read().split()[:3]
        avg_keys = ['1m', '5m', '15m']
        avg_dict = dict(zip(avg_keys, avgs))
        # Check each entry for threshold
        if float(avgs[0]) < float(config[0]['1m'][0]) or \
        float(avgs[0]) > float(config[0]['1m'][1]) or \
        float(avgs[1]) < float(config[1]['5m'][0]) or \
        float(avgs[1]) > float(config[1]['5m'][1]) or \
        float(avgs[2]) < float(config[2]['15m'][0]) or \
        float(avgs[2]) > float(config[2]['15m'][1]):
            ret.append(avg_dict)
    return ret