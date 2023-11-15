def event(tagmatch='*',
        count=-1,
        quiet=False,
        sock_dir=None,
        pretty=False,
        node='minion'):
    r'''
    Watch Salt's event bus and block until the given tag is matched

    .. versionadded:: 2016.3.0

    This is useful for utilizing Salt's event bus from shell scripts or for
    taking simple actions directly from the CLI.

    Enable debug logging to see ignored events.

    :param tagmatch: the event is written to stdout for each tag that matches
        this pattern; uses the same matching semantics as Salt's Reactor.
    :param count: this number is decremented for each event that matches the
        ``tagmatch`` parameter; pass ``-1`` to listen forever.
    :param quiet: do not print to stdout; just block
    :param sock_dir: path to the Salt master's event socket file.
    :param pretty: Output the JSON all on a single line if ``False`` (useful
        for shell tools); pretty-print the JSON output if ``True``.
    :param node: Watch the minion-side or master-side event bus.

    CLI Example:

    .. code-block:: bash

        salt-call --local state.event pretty=True
    '''
    sevent = salt.utils.event.get_event(
            node,
            sock_dir or __opts__['sock_dir'],
            __opts__['transport'],
            opts=__opts__,
            listen=True)

    while True:
        ret = sevent.get_event(full=True, auto_reconnect=True)
        if ret is None:
            continue

        if fnmatch.fnmatch(ret['tag'], tagmatch):
            if not quiet:
                print('{0}\t{1}'.format(
                    ret['tag'],
                    json.dumps(
                        ret['data'],
                        sort_keys=pretty,
                        indent=None if not pretty else 4)))
                sys.stdout.flush()

            count -= 1
            log.debug('Remaining event matches: %s', count)

            if count == 0:
                break
        else:
            log.debug('Skipping event tag: %s', ret['tag'])
            continue