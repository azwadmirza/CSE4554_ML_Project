    def notify_spyder(self, frame):
        if not frame:
            return

        if IS_IPYKERNEL:
            from IPython.core.getipython import get_ipython
            ipython_shell = get_ipython()
        else:
            ipython_shell = None

        # Get filename and line number of the current frame
        fname = self.canonic(frame.f_code.co_filename)
        if PY2:
            try:
                fname = unicode(fname, "utf-8")
            except TypeError:
                pass
        lineno = frame.f_lineno

        # Set step of the current frame (if any)
        step = {}
        if isinstance(fname, basestring) and isinstance(lineno, int):
            if osp.isfile(fname):
                if ipython_shell:
                    step = dict(fname=fname, lineno=lineno)
                elif monitor is not None:
                    monitor.notify_pdb_step(fname, lineno)
                    time.sleep(0.1)

        # Publish Pdb state so we can update the Variable Explorer
        # and the Editor on the Spyder side
        if ipython_shell:
            ipython_shell.kernel._pdb_step = step
            ipython_shell.kernel.publish_pdb_state()