def _handle_signals(client, signum, sigframe):
    trace = traceback.format_exc()
    try:
        hardcrash = client.options.hard_crash
    except (AttributeError, KeyError):
        hardcrash = False

    if signum == signal.SIGINT:
        exit_msg = '\nExiting gracefully on Ctrl-c'
        try:
            jid = client.local_client.pub_data['jid']
            exit_msg += (
                '\n'
                'This job\'s jid is: {0}\n'
                'The minions may not have all finished running and any remaining '
                'minions will return upon completion. To look up the return data '
                'for this job later, run the following command:\n\n'
                'salt-run jobs.lookup_jid {0}'.format(jid)
            )
        except (AttributeError, KeyError):
            pass
    else:
        exit_msg = None

    _handle_interrupt(
        SystemExit(exit_msg),
        Exception('\nExiting with hard crash on Ctrl-c'),
        hardcrash, trace=trace)