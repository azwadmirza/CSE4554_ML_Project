    def run_file(self, debug=False):
        """Run script inside current interpreter or in a new one"""
        editorstack = self.get_current_editorstack()
        if editorstack.save():
            editor = self.get_current_editor()
            fname = osp.abspath(self.get_current_filename())

            # Get fname's dirname before we escape the single and double
            # quotes (Fixes Issue #6771)
            dirname = osp.dirname(fname)

            # Escape single and double quotes in fname and dirname
            # (Fixes Issue #2158)
            fname = fname.replace("'", r"\'").replace('"', r'\"')
            dirname = dirname.replace("'", r"\'").replace('"', r'\"')

            runconf = get_run_configuration(fname)
            if runconf is None:
                dialog = RunConfigOneDialog(self)
                dialog.size_change.connect(lambda s: self.set_dialog_size(s))
                if self.dialog_size is not None:
                    dialog.resize(self.dialog_size)
                dialog.setup(fname)
                if CONF.get('run', 'open_at_least_once',
                            not running_under_pytest()):
                    # Open Run Config dialog at least once: the first time 
                    # a script is ever run in Spyder, so that the user may 
                    # see it at least once and be conscious that it exists
                    show_dlg = True
                    CONF.set('run', 'open_at_least_once', False)
                else:
                    # Open Run Config dialog only 
                    # if ALWAYS_OPEN_FIRST_RUN_OPTION option is enabled
                    show_dlg = CONF.get('run', ALWAYS_OPEN_FIRST_RUN_OPTION)
                if show_dlg and not dialog.exec_():
                    return
                runconf = dialog.get_configuration()

            args = runconf.get_arguments()
            python_args = runconf.get_python_arguments()
            interact = runconf.interact
            post_mortem = runconf.post_mortem
            current = runconf.current
            systerm = runconf.systerm
            clear_namespace = runconf.clear_namespace

            if runconf.file_dir:
                wdir = dirname
            elif runconf.cw_dir:
                wdir = ''
            elif osp.isdir(runconf.dir):
                wdir = runconf.dir
            else:
                wdir = ''

            python = True # Note: in the future, it may be useful to run
            # something in a terminal instead of a Python interp.
            self.__last_ec_exec = (fname, wdir, args, interact, debug,
                                   python, python_args, current, systerm, 
                                   post_mortem, clear_namespace)
            self.re_run_file()
            if not interact and not debug:
                # If external console dockwidget is hidden, it will be
                # raised in top-level and so focus will be given to the
                # current external shell automatically
                # (see SpyderPluginWidget.visibility_changed method)
                editor.setFocus()