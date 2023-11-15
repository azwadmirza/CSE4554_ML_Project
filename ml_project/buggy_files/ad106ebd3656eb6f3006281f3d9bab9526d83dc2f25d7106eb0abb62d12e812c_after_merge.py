def aggregate_issues(conf, main_section, debug):
    """ Return all issues from every target. """
    log.info("Starting to aggregate remote issues.")

    # Create and call service objects for every target in the config
    targets = aslist(conf.get(main_section, 'targets'))

    queue = multiprocessing.Queue()

    log.info("Spawning %i workers." % len(targets))
    processes = []

    if debug:
        for target in targets:
            _aggregate_issues(
                conf,
                main_section,
                target,
                queue,
                conf.get(target, 'service')
            )
    else:
        for target in targets:
            proc = multiprocessing.Process(
                target=_aggregate_issues,
                args=(conf, main_section, target, queue, conf.get(target, 'service'))
            )
            proc.start()
            processes.append(proc)

            # Sleep for 1 second here to try and avoid a race condition where
            # all N workers start up and ask the gpg-agent process for
            # information at the same time.  This causes gpg-agent to fumble
            # and tell some of our workers some incomplete things.
            time.sleep(1)

    currently_running = len(targets)
    while currently_running > 0:
        issue = queue.get(True)
        if isinstance(issue, tuple):
            completion_type, args = issue
            if completion_type == SERVICE_FINISHED_ERROR:
                target, e = args
                log.info("Terminating workers")
                for process in processes:
                    process.terminate()
                raise RuntimeError(
                    "critical error in target '{}'".format(target))
            currently_running -= 1
            continue
        yield issue

    log.info("Done aggregating remote issues.")