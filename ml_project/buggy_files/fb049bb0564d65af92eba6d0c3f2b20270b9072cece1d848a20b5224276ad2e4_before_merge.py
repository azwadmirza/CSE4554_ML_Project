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
        if len(rcc_files) > 0:
            rcc_kwargs = {'output' : '@BASENAME@.cpp',
                          'arguments' : ['@INPUT@', '-o', '@OUTPUT@']}
            rcc_gen = build.Generator([self.rcc], rcc_kwargs)
            rcc_output = build.GeneratedList(rcc_gen)
            qrc_deps = []
            for i in rcc_files:
                qrc_deps += self.parse_qrc(state, i)
            rcc_output.extra_depends = qrc_deps
            [rcc_output.add_file(os.path.join(state.subdir, a)) for a in rcc_files]
            sources.append(rcc_output)
        if len(ui_files) > 0:
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