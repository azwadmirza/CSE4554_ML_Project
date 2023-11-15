    def update(self, config, srcdir, doctreedir, app):
        """(Re-)read all files new or changed since last update.

        Store all environment docnames in the canonical format (ie using SEP as
        a separator in place of os.path.sep).
        """
        config_changed = False
        if self.config is None:
            msg = '[new config] '
            config_changed = True
        else:
            # check if a config value was changed that affects how
            # doctrees are read
            for key, descr in iteritems(config.values):
                if descr[1] != 'env':
                    continue
                if self.config[key] != config[key]:
                    msg = '[config changed] '
                    config_changed = True
                    break
            else:
                msg = ''
            # this value is not covered by the above loop because it is handled
            # specially by the config class
            if self.config.extensions != config.extensions:
                msg = '[extensions changed] '
                config_changed = True
        # the source and doctree directories may have been relocated
        self.srcdir = srcdir
        self.doctreedir = doctreedir
        self.find_files(config)
        self.config = config

        # this cache also needs to be updated every time
        self._nitpick_ignore = set(self.config.nitpick_ignore)

        app.info(bold('updating environment: '), nonl=1)

        added, changed, removed = self.get_outdated_files(config_changed)

        # allow user intervention as well
        for docs in app.emit('env-get-outdated', self, added, changed, removed):
            changed.update(set(docs) & self.found_docs)

        # if files were added or removed, all documents with globbed toctrees
        # must be reread
        if added or removed:
            # ... but not those that already were removed
            changed.update(self.glob_toctrees & self.found_docs)

        msg += '%s added, %s changed, %s removed' % (len(added), len(changed),
                                                     len(removed))
        app.info(msg)

        self.app = app

        # clear all files no longer present
        for docname in removed:
            app.emit('env-purge-doc', self, docname)
            self.clear_doc(docname)

        # read all new and changed files
        docnames = sorted(added | changed)
        # allow changing and reordering the list of docs to read
        app.emit('env-before-read-docs', self, docnames)

        # check if we should do parallel or serial read
        par_ok = False
        if parallel_available and len(docnames) > 5 and app.parallel > 1:
            par_ok = True
            for extname, md in app._extension_metadata.items():
                ext_ok = md.get('parallel_read_safe')
                if ext_ok:
                    continue
                if ext_ok is None:
                    app.warn('the %s extension does not declare if it '
                             'is safe for parallel reading, assuming it '
                             'isn\'t - please ask the extension author to '
                             'check and make it explicit' % extname)
                    app.warn('doing serial read')
                else:
                    app.warn('the %s extension is not safe for parallel '
                             'reading, doing serial read' % extname)
                par_ok = False
                break
        if par_ok:
            self._read_parallel(docnames, app, nproc=app.parallel)
        else:
            self._read_serial(docnames, app)

        if config.master_doc not in self.all_docs:
            self.warn(None, 'master file %s not found' %
                      self.doc2path(config.master_doc))

        self.app = None

        for retval in app.emit('env-updated', self):
            if retval is not None:
                docnames.extend(retval)

        return sorted(docnames)