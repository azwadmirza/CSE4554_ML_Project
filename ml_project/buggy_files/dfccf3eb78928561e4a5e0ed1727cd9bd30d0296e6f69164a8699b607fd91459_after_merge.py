    def new(self, fname=None, editorstack=None, text=None):
        """
        Create a new file - Untitled

        fname=None --> fname will be 'untitledXX.py' but do not create file
        fname=<basestring> --> create file
        """
        # If no text is provided, create default content
        empty = False
        try:
            if text is None:
                default_content = True
                text, enc = encoding.read(self.TEMPLATE_PATH)
                enc_match = re.search(r'-*- coding: ?([a-z0-9A-Z\-]*) -*-',
                                      text)
                if enc_match:
                    enc = enc_match.group(1)
                # Initialize template variables
                # Windows
                username = encoding.to_unicode_from_fs(
                                os.environ.get('USERNAME', ''))
                # Linux, Mac OS X
                if not username:
                    username = encoding.to_unicode_from_fs(
                                   os.environ.get('USER', '-'))
                VARS = {
                    'date': time.ctime(),
                    'username': username,
                }
                try:
                    text = text % VARS
                except Exception:
                    pass
            else:
                default_content = False
                enc = encoding.read(self.TEMPLATE_PATH)[1]
        except (IOError, OSError):
            text = ''
            enc = 'utf-8'
            default_content = True
            empty = True

        create_fname = lambda n: to_text_string(_("untitled")) + ("%d.py" % n)
        # Creating editor widget
        if editorstack is None:
            current_es = self.get_current_editorstack()
        else:
            current_es = editorstack
        created_from_here = fname is None
        if created_from_here:
            if self.untitled_num == 0:
                for finfo in current_es.data:
                    current_filename = finfo.editor.filename
                    if _("untitled") in current_filename:
                        # Start the counter of the untitled_num with respect
                        # to this number if there's other untitled file in
                        # spyder. Please see spyder-ide/spyder#7831
                        fname_data = osp.splitext(current_filename)
                        try:
                            act_num = int(
                                fname_data[0].split(_("untitled"))[-1])
                            self.untitled_num = act_num + 1
                        except ValueError:
                            # Catch the error in case the user has something
                            # different from a number after the untitled
                            # part.
                            # Please see spyder-ide/spyder#12892
                            self.untitled_num = 0
            while True:
                fname = create_fname(self.untitled_num)
                self.untitled_num += 1
                if not osp.isfile(fname):
                    break
            basedir = getcwd_or_home()

            if self.main.projects.get_active_project() is not None:
                basedir = self.main.projects.get_active_project_path()
            else:
                c_fname = self.get_current_filename()
                if c_fname is not None and c_fname != self.TEMPFILE_PATH:
                    basedir = osp.dirname(c_fname)
            fname = osp.abspath(osp.join(basedir, fname))
        else:
            # QString when triggered by a Qt signal
            fname = osp.abspath(to_text_string(fname))
            index = current_es.has_filename(fname)
            if index is not None and not current_es.close_file(index):
                return

        # Creating the editor widget in the first editorstack (the one that
        # can't be destroyed), then cloning this editor widget in all other
        # editorstacks:
        # Setting empty to True by default to avoid the additional space
        # created at the end of the templates.
        # See: spyder-ide/spyder#12596
        finfo = self.editorstacks[0].new(fname, enc, text, default_content,
                                         empty=True)
        finfo.path = self.main.get_spyder_pythonpath()
        self._clone_file_everywhere(finfo)
        current_editor = current_es.set_current_filename(finfo.filename)
        self.register_widget_shortcuts(current_editor)
        if not created_from_here:
            self.save(force=True)