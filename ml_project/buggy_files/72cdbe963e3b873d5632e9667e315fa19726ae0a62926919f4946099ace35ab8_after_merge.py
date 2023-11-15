def start(docker_url='unix://var/run/docker.sock',
          timeout=CLIENT_TIMEOUT,
          tag='salt/engines/docker_events'):
    '''
    Scan for Docker events and fire events

    Example Config

    .. code-block:: yaml

        engines:
          docker_events:
            docker_url: unix://var/run/docker.sock

    The config above sets up engines to listen
    for events from the Docker daemon and publish
    them to the Salt event bus.
    '''

    if __opts__.get('__role') == 'master':
        fire_master = salt.utils.event.get_master_event(
            __opts__,
            __opts__['sock_dir']).fire_event
    else:
        fire_master = None

    def fire(tag, msg):
        '''
        How to fire the event
        '''
        if fire_master:
            fire_master(msg, tag)
        else:
            __salt__['event.send'](tag, msg)

    client = docker.Client(base_url=docker_url,
                           timeout=timeout)
    try:
        events = client.events()
        for event in events:
            data = json.loads(event.decode(__salt_system_encoding__, errors='replace'))
            fire('{0}/{1}'.format(tag, data['status']), data)
    except Exception:
        traceback.print_exc()