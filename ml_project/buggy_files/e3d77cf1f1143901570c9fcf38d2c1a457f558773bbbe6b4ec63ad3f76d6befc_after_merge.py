    def doPostPluginsInit(self):
        """Create a Leo window for each file in the lm.files list."""
        # Clear g.app.initing _before_ creating commanders.
        lm = self
        g.app.initing = False # "idle" hooks may now call g.app.forceShutdown.
        # Create the main frame.  Show it and all queued messages.
        c = c1 = fn = None
        if lm.files:
            try: # #1403.
                for n, fn in enumerate(lm.files):
                    lm.more_cmdline_files = n < len(lm.files) - 1
                    c = lm.loadLocalFile(fn, gui=g.app.gui, old_c=None)
                        # Returns None if the file is open in another instance of Leo.
            except Exception:
                g.es_print(f"Unexpected exception reading {fn!r}")
                g.es_exception()
                c = None
            if c and not c1:
                c1 = c
        g.app.loaded_session = not lm.files
            # Load (and save later) a session only no files were given on the command line.
        if g.app.sessionManager and g.app.loaded_session:
            try: # #1403.
                aList = g.app.sessionManager.load_snapshot()
                if aList:
                    g.app.sessionManager.load_session(c1, aList)
                    # tag:#659.
                    if g.app.windowList:
                        c = c1 = g.app.windowList[0].c
                    else:
                        c = c1 = None
            except Exception:
                g.es_print('unexpected exception loading session')
                g.es_exception()
        # Enable redraws.
        g.app.disable_redraw = False
        if not c1 or not g.app.windowList:
            try: # #1403.
                c1 = lm.openEmptyWorkBook()
                    # Calls LM.loadLocalFile.
            except Exception:
                g.es_print('unexpected exception reading empty workbook')
                g.es_exception()
        # Fix bug #199.
        g.app.runAlreadyOpenDialog(c1)
        # Put the focus in the first-opened file.
        fileName = lm.files[0] if lm.files else None
        c = c1
        # For qt gui, select the first-loaded tab.
        if g.app.use_global_docks:
            pass
        else:
            if hasattr(g.app.gui, 'frameFactory'):
                factory = g.app.gui.frameFactory
                if factory and hasattr(factory, 'setTabForCommander'):
                    factory.setTabForCommander(c)
        if not c:
            return False # Force an immediate exit.
        # Fix bug 844953: tell Unity which menu to use.
            # if c: c.enableMenuBar()
        # Do the final inits.
        g.app.logInited = True
        g.app.initComplete = True
        if c:
            c.setLog()
            c.redraw()
        p = c.p if c else None
        g.doHook("start2", c=c, p=p, fileName=fileName)
        if c:
            c.initialFocusHelper()
        screenshot_fn = lm.options.get('screenshot_fn')
        if screenshot_fn:
            lm.make_screen_shot(screenshot_fn)
            return False # Force an immediate exit.
        return True