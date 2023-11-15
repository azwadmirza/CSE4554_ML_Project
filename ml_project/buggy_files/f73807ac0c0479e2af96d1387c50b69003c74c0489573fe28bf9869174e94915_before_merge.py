    def read_doc(self, docname, src_path=None, save_parsed=True, app=None):
        """Parse a file and add/update inventory entries for the doctree.

        If srcpath is given, read from a different source file.
        """
        # remove all inventory entries for that file
        if app:
            app.emit('env-purge-doc', self, docname)

        self.clear_doc(docname)

        if src_path is None:
            src_path = self.doc2path(docname)

        self.temp_data['docname'] = docname
        # defaults to the global default, but can be re-set in a document
        self.temp_data['default_domain'] = \
            self.domains.get(self.config.primary_domain)

        self.settings['input_encoding'] = self.config.source_encoding
        self.settings['trim_footnote_reference_space'] = \
            self.config.trim_footnote_reference_space
        self.settings['gettext_compact'] = self.config.gettext_compact

        self.patch_lookup_functions()

        if self.config.default_role:
            role_fn, messages = roles.role(self.config.default_role, english,
                                           0, dummy_reporter)
            if role_fn:
                roles._roles[''] = role_fn
            else:
                self.warn(docname, 'default role %s not found' %
                          self.config.default_role)

        codecs.register_error('sphinx', self.warn_and_replace)

        class SphinxSourceClass(FileInput):
            def __init__(self_, *args, **kwds):
                # don't call sys.exit() on IOErrors
                kwds['handle_io_errors'] = False
                FileInput.__init__(self_, *args, **kwds)

            def decode(self_, data):
                if isinstance(data, text_type):
                    return data
                return data.decode(self_.encoding, 'sphinx')

            def read(self_):
                data = FileInput.read(self_)
                if app:
                    arg = [data]
                    app.emit('source-read', docname, arg)
                    data = arg[0]
                if self.config.rst_epilog:
                    data = data + '\n' + self.config.rst_epilog + '\n'
                if self.config.rst_prolog:
                    data = self.config.rst_prolog + '\n' + data
                return data

        # publish manually
        pub = Publisher(reader=SphinxStandaloneReader(),
                        writer=SphinxDummyWriter(),
                        source_class=SphinxSourceClass,
                        destination_class=NullOutput)
        pub.set_components(None, 'restructuredtext', None)
        pub.process_programmatic_settings(None, self.settings, None)
        pub.set_source(None, src_path.encode(fs_encoding))
        pub.set_destination(None, None)
        pub.publish()
        doctree = pub.document

        # post-processing
        self.filter_messages(doctree)
        self.process_dependencies(docname, doctree)
        self.process_images(docname, doctree)
        self.process_downloads(docname, doctree)
        self.process_metadata(docname, doctree)
        self.process_refonly_bullet_lists(docname, doctree)
        self.create_title_from(docname, doctree)
        self.note_indexentries_from(docname, doctree)
        self.note_citations_from(docname, doctree)
        self.build_toc_from(docname, doctree)
        for domain in itervalues(self.domains):
            domain.process_doc(self, docname, doctree)

        # allow extension-specific post-processing
        if app:
            app.emit('doctree-read', doctree)

        # store time of build, for outdated files detection
        # (Some filesystems have coarse timestamp resolution;
        # therefore time.time() can be older than filesystem's timestamp.
        # For example, FAT32 has 2sec timestamp resolution.)
        self.all_docs[docname] = max(
                time.time(), path.getmtime(self.doc2path(docname)))

        if self.versioning_condition:
            # get old doctree
            try:
                f = open(self.doc2path(docname,
                                       self.doctreedir, '.doctree'), 'rb')
                try:
                    old_doctree = pickle.load(f)
                finally:
                    f.close()
            except EnvironmentError:
                old_doctree = None

            # add uids for versioning
            if old_doctree is None:
                list(add_uids(doctree, self.versioning_condition))
            else:
                list(merge_doctrees(
                    old_doctree, doctree, self.versioning_condition))

        # make it picklable
        doctree.reporter = None
        doctree.transformer = None
        doctree.settings.warning_stream = None
        doctree.settings.env = None
        doctree.settings.record_dependencies = None
        for metanode in doctree.traverse(MetaBody.meta):
            # docutils' meta nodes aren't picklable because the class is nested
            metanode.__class__ = addnodes.meta

        # cleanup
        self.temp_data.clear()

        if save_parsed:
            # save the parsed doctree
            doctree_filename = self.doc2path(docname, self.doctreedir,
                                             '.doctree')
            dirname = path.dirname(doctree_filename)
            if not path.isdir(dirname):
                os.makedirs(dirname)
            f = open(doctree_filename, 'wb')
            try:
                pickle.dump(doctree, f, pickle.HIGHEST_PROTOCOL)
            finally:
                f.close()
        else:
            return doctree