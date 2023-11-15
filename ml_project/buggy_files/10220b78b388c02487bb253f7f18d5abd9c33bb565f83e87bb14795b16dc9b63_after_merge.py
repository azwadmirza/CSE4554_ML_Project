        def terminate_now(signum, _):
            ivre.utils.LOGGER.info('shutdown: got signal %d, halting now.',
                                   signum)
            exit()