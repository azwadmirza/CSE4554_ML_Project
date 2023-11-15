    def _run_with_debugger(self, code, code_ns, filename=None,
                           bp_line=None, bp_file=None):
        """
        Run `code` in debugger with a break point.

        Parameters
        ----------
        code : str
            Code to execute.
        code_ns : dict
            A namespace in which `code` is executed.
        filename : str
            `code` is ran as if it is in `filename`.
        bp_line : int, optional
            Line number of the break point.
        bp_file : str, optional
            Path to the file in which break point is specified.
            `filename` is used if not given.

        Raises
        ------
        UsageError
            If the break point given by `bp_line` is not valid.

        """
        deb = self.shell.InteractiveTB.pdb
        if not deb:
            self.shell.InteractiveTB.pdb = self.shell.InteractiveTB.debugger_cls()
            deb = self.shell.InteractiveTB.pdb

        # reset Breakpoint state, which is moronically kept
        # in a class
        bdb.Breakpoint.next = 1
        bdb.Breakpoint.bplist = {}
        bdb.Breakpoint.bpbynumber = [None]
        if bp_line is not None:
            # Set an initial breakpoint to stop execution
            maxtries = 10
            bp_file = bp_file or filename
            checkline = deb.checkline(bp_file, bp_line)
            if not checkline:
                for bp in range(bp_line + 1, bp_line + maxtries + 1):
                    if deb.checkline(bp_file, bp):
                        break
                else:
                    msg = ("\nI failed to find a valid line to set "
                           "a breakpoint\n"
                           "after trying up to line: %s.\n"
                           "Please set a valid breakpoint manually "
                           "with the -b option." % bp)
                    raise UsageError(msg)
            # if we find a good linenumber, set the breakpoint
            deb.do_break('%s:%s' % (bp_file, bp_line))

        if filename:
            # Mimic Pdb._runscript(...)
            deb._wait_for_mainpyfile = True
            deb.mainpyfile = deb.canonic(filename)

        # Start file run
        print("NOTE: Enter 'c' at the %s prompt to continue execution." % deb.prompt)
        try:
            if filename:
                # save filename so it can be used by methods on the deb object
                deb._exec_filename = filename
            while True:
                try:
                    deb.run(code, code_ns)
                except Restart:
                    print("Restarting")
                    if filename:
                        deb._wait_for_mainpyfile = True
                        deb.mainpyfile = deb.canonic(filename)
                    continue
                else:
                    break
            

        except:
            etype, value, tb = sys.exc_info()
            # Skip three frames in the traceback: the %run one,
            # one inside bdb.py, and the command-line typed by the
            # user (run by exec in pdb itself).
            self.shell.InteractiveTB(etype, value, tb, tb_offset=3)