    def _kill_kernel(self):
        """
        Kill the running kernel.

        Override private method to be able to correctly close kernel that was
        started via a batch/bash script for correct conda env activation.
        """
        if self.has_kernel:

            # Signal the kernel to terminate (sends SIGKILL on Unix and calls
            # TerminateProcess() on Win32).
            try:
                if hasattr(signal, 'SIGKILL'):
                    self.signal_kernel(signal.SIGKILL)
                else:
                    # This is the additional line that was added to properly
                    # kill the spyder started kernels.
                    self.kill_proc_tree(self.kernel.pid)

                    self.kernel.kill()
            except OSError as e:
                # In Windows, we will get an Access Denied error if the process
                # has already terminated. Ignore it.
                if sys.platform == 'win32':
                    if e.winerror != 5:
                        raise
                # On Unix, we may get an ESRCH error if the process has already
                # terminated. Ignore it.
                else:
                    from errno import ESRCH
                    if e.errno != ESRCH:
                        raise

            # Block until the kernel terminates.
            self.kernel.wait()
            self.kernel = None
        else:
            raise RuntimeError("Cannot kill kernel. No kernel is running!")