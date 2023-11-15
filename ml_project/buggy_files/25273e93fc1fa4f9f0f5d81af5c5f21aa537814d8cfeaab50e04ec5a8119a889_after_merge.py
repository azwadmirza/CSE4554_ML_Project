        def terminate(signum, _):
            global WANT_DOWN
            ivre.utils.LOGGER.info(
                'shutdown: got signal %d, will halt after current task.',
                signum,
            )
            WANT_DOWN = True