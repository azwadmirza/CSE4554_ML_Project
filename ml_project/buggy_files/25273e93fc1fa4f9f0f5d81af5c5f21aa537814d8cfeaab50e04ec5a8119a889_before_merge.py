        def terminate(signum, _):
            global WANT_DOWN
            print('SHUTDOWN: got signal %d, will halt after current '
                  'task.' % signum)
            WANT_DOWN = True