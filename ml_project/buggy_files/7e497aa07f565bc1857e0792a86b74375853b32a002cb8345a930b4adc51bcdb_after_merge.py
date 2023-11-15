    def _func_custom_target_impl(self, node, args, kwargs):
        'Implementation-only, without FeatureNew checks, for internal use'
        name = args[0]
        kwargs['install_mode'] = self._get_kwarg_install_mode(kwargs)
        if 'input' in kwargs:
            try:
                kwargs['input'] = self.source_strings_to_files(extract_as_list(kwargs, 'input'))
            except mesonlib.MesonException:
                mlog.warning('''Custom target input \'%s\' can\'t be converted to File object(s).
This will become a hard error in the future.''' % kwargs['input'])
        tg = CustomTargetHolder(build.CustomTarget(name, self.subdir, self.subproject, kwargs), self)
        self.add_target(name, tg.held_object)
        return tg