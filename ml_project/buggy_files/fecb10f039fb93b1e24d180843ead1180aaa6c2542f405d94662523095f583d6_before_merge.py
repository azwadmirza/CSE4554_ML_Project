def main():
    try:
        import argparse
        parser = argparse.ArgumentParser(
            description=__doc__,
            parents=[ivre.target.argparser])
    except ImportError:
        import optparse
        parser = optparse.OptionParser(
            description=__doc__)
        for args, kargs in ivre.target.argparser.args:
            parser.add_option(*args, **kargs)
        parser.parse_args_orig = parser.parse_args
        parser.parse_args = lambda: parser.parse_args_orig()[0]
        parser.add_argument = parser.add_option
    parser.add_argument(
        '--assign-free-agents', action="store_true",
        help="Assign any agent available (only useful when specifying"
        " a target)."
    )
    parser.add_argument(
        '--max-waiting', metavar='COUNT', type=int, default=60,
        help='Maximum targets waiting (only affects --add-agent)'
    )
    parser.add_argument(
        '--source', metavar='NAME',
        help='Source name (only affects --add-agent)'
    )
    parser.add_argument('--add-agent', metavar='(HOST:)PATH', nargs='+')
    parser.add_argument('--del-agent', metavar='AGENT', nargs='+')
    parser.add_argument('--add-local-master', action="store_true")
    parser.add_argument('--master-path', metavar="PATH",
                        default=ivre.config.AGENT_MASTER_PATH,
                        help="Non-default path to use for master "
                        "(default is specified by the configuration "
                        "attribute `AGENT_MASTER_PATH`)")
    parser.add_argument('--list-agents', action="store_true")
    parser.add_argument('--list-scans', action="store_true")
    parser.add_argument('--list-masters', action="store_true")
    parser.add_argument('--assign', metavar="AGENT:SCAN")
    parser.add_argument('--unassign', metavar="AGENT")
    parser.add_argument('--init', action="store_true",
                        help='Purge or create and initialize the database.')
    parser.add_argument('--sleep', type=int, default=2,
                        help='Time to wait between each feed/sync '
                        'cycle (only usefull with --daemon).')
    parser.add_argument(
        '--daemon', action="store_true", help="""Run continuously
        feed/sync cycles. The "sync" part requires to be able to rsync
        to & from the agents non-interactively (without entering a
        password). Please note this will *not* daemonize the
        process.

        """)
    args = parser.parse_args()

    if args.init:
        if os.isatty(sys.stdin.fileno()):
            sys.stdout.write(
                'This will remove any agent and/or scan in your '
                'database and files. Process ? [y/N] ')
            ans = input()
            if ans.lower() != 'y':
                sys.exit(-1)
        ivre.db.db.agent.init()
        ivre.utils.cleandir(args.master_path)
        for dirname in ["output", "onhold"]:
            ivre.utils.makedirs(
                os.path.join(args.master_path, dirname)
            )

    if args.add_local_master:
        ivre.utils.makedirs(args.master_path)
        ivre.db.db.agent.add_local_master(args.master_path)

    if args.add_agent is not None:
        masterid = ivre.db.db.agent.masterid_from_dir(args.master_path)
        for agent in args.add_agent:
            ivre.db.db.agent.add_agent_from_string(
                masterid, agent,
                maxwaiting=args.max_waiting,
                source=args.source,
            )

    if args.del_agent is not None:
        for agentid in args.del_agent:
            ivre.db.db.agent.del_agent(ivre.db.db.agent.str2id(agentid))

    if args.assign is not None:
        try:
            agentid, scanid = (ivre.db.db.agent.str2id(elt) for elt in
                               args.assign.split(':', 1))
        except ValueError:
            parser.error("argument --assign: must give agentid:scanid")
        ivre.db.db.agent.assign_agent(agentid, scanid)

    if args.unassign is not None:
        ivre.db.db.agent.unassign_agent(ivre.db.db.agent.str2id(args.unassign))

    targets = ivre.target.target_from_args(args)
    if targets is not None:
        ivre.db.db.agent.add_scan(
            targets,
            assign_to_free_agents=bool(args.assign_free_agents)
        )

    if args.list_agents:
        for agent in (ivre.db.db.agent.get_agent(agentid)
                      for agentid in ivre.db.db.agent.get_agents()):
            display_agent(agent)

    if args.list_scans:
        for scan in (ivre.db.db.agent.get_scan(scanid)
                     for scanid in ivre.db.db.agent.get_scans()):
            display_scan(scan)

    if args.list_masters:
        for master in (ivre.db.db.agent.get_master(masterid)
                       for masterid in ivre.db.db.agent.get_masters()):
            display_master(master)

    if args.daemon:
        def terminate(signum, _):
            global WANT_DOWN
            print('SHUTDOWN: got signal %d, will halt after current '
                  'task.' % signum)
            WANT_DOWN = True
        def terminate_now(signum, _):
            print('SHUTDOWN: got signal %d, halting now.' % signum)
            exit()
        signal.signal(signal.SIGINT, terminate)
        signal.signal(signal.SIGTERM, terminate)

        masterid = ivre.db.db.agent.masterid_from_dir(args.master_path)
        while not WANT_DOWN:
            ivre.db.db.agent.feed_all(masterid)
            ivre.db.db.agent.sync_all(masterid)
            signal.signal(signal.SIGINT, terminate_now)
            signal.signal(signal.SIGTERM, terminate_now)
            if not WANT_DOWN:
                time.sleep(args.sleep)
            signal.signal(signal.SIGINT, terminate)
            signal.signal(signal.SIGTERM, terminate)