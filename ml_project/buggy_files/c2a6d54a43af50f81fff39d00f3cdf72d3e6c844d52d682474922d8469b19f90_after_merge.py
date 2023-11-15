        def give_terminal_to(pgid):
            oldmask = signal.pthread_sigmask(signal.SIG_BLOCK,
                                             _block_when_giving)
            if pgid is None:
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
                return False
            try:
                os.tcsetpgrp(FD_STDERR, pgid)
                return True
            except OSError as e:
                if e.errno == 22:  # [Errno 22] Invalid argument
                    # there are cases that all the processes of pgid have
                    # finished, then we don't need to do anything here, see
                    # issue #2220
                    return False
                elif e.errno == 25:  # [Errno 25] Inappropriate ioctl for device
                    # There are also cases where we are not connected to a
                    # real TTY, even though we may be run in interactive
                    # mode. See issue #2267 for an example with emacs
                    return False
                else:
                    raise
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)