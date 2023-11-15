        def give_terminal_to(pgid):
            oldmask = signal.pthread_sigmask(signal.SIG_BLOCK,
                                             _block_when_giving)
            os.tcsetpgrp(sys.stderr.fileno(), pgid)
            signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
            return True