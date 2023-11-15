    def preprocess(self, state, args, kwargs):
        rcc_files = kwargs.pop('qresources', [])
        if not isinstance(rcc_files, list):
            rcc_files = [rcc_files]
        ui_files = kwargs.pop('ui_files', [])
        if not isinstance(ui_files, list):
            ui_files = [ui_files]
        moc_headers = kwargs.pop('moc_headers', [])
        if not isinstance(moc_headers, list):
            moc_headers = [moc_headers]
        moc_sources = kwargs.pop('moc_sources', [])
        if not isinstance(moc_sources, list):
            moc_sources = [moc_sources]
        srctmp = kwargs.pop('sources', [])
        if not isinstance(srctmp, list):
            srctmp = [srctmp]
        sources = args[1:] + srctmp
        self._detect_tools(state.environment)
        err_msg = "{0} sources specified and couldn't find {1}, " \
                  "please check your qt5 installation"
        if len(moc_headers) + len(moc_sources) > 0 and not self.moc.found():
            raise MesonException(err_msg.format('MOC', 'moc-qt5'))
        if len(rcc_files) > 0:
            if not self.rcc.found():
                raise MesonException(err_msg.format('RCC', 'rcc-qt5'))
            qrc_deps = []
            for i in rcc_files:
                qrc_deps += self.parse_qrc(state, i)
            basename = os.path.split(rcc_files[0])[1]
            rcc_kwargs = {'input' : rcc_files,
                    'output' : basename + '.cpp',
                    'command' : [self.rcc, '-o', '@OUTPUT@', '@INPUT@'],
                    'depend_files' : qrc_deps,
                    }
            name = 'qt5-' + basename.replace('.', '_')
            res_target = build.CustomTarget(name, state.subdir, rcc_kwargs)
            sources.append(res_target)
        if len(ui_files) > 0:
            if not self.uic.found():
                raise MesonException(err_msg.format('UIC', 'uic-qt5'))
            ui_kwargs = {'output' : 'ui_@BASENAME@.h',
                         'arguments' : ['-o', '@OUTPUT@', '@INPUT@']}
            ui_gen = build.Generator([self.uic], ui_kwargs)
            ui_output = build.GeneratedList(ui_gen)
            [ui_output.add_file(os.path.join(state.subdir, a)) for a in ui_files]
            sources.append(ui_output)
        if len(moc_headers) > 0:
            moc_kwargs = {'output' : 'moc_@BASENAME@.cpp',
                          'arguments' : ['@INPUT@', '-o', '@OUTPUT@']}
            moc_gen = build.Generator([self.moc], moc_kwargs)
            moc_output = build.GeneratedList(moc_gen)
            [moc_output.add_file(os.path.join(state.subdir, a)) for a in moc_headers]
            sources.append(moc_output)
        if len(moc_sources) > 0:
            moc_kwargs = {'output' : '@BASENAME@.moc',
                          'arguments' : ['@INPUT@', '-o', '@OUTPUT@']}
            moc_gen = build.Generator([self.moc], moc_kwargs)
            moc_output = build.GeneratedList(moc_gen)
            [moc_output.add_file(os.path.join(state.subdir, a)) for a in moc_sources]
            sources.append(moc_output)
        return sources