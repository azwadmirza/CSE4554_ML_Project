    def notify_spyder(self, frame):
        if not frame:
            return
        fname = self.canonic(frame.f_code.co_filename)
        if PY2:
            try:
                fname = unicode(fname, "utf-8")
            except TypeError:
                pass
        lineno = frame.f_lineno
        if isinstance(fname, basestring) and isinstance(lineno, int):
            if osp.isfile(fname):
                if IS_IPYKERNEL:
                    from IPython.core.getipython import get_ipython
                    ipython_shell = get_ipython()
                    if ipython_shell:
                        step = dict(fname=fname, lineno=lineno)
                        ipython_shell.kernel._pdb_step = step
                elif monitor is not None:
                    monitor.notify_pdb_step(fname, lineno)
                    time.sleep(0.1)