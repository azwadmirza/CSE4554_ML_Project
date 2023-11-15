        def terminate_now(signum, _):
            print('SHUTDOWN: got signal %d, halting now.' % signum)
            exit()