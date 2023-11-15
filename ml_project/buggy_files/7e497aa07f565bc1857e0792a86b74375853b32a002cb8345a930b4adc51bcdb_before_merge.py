    def _func_custom_target_impl(self, node, args, kwargs):
        'Implementation-only, without FeatureNew checks, for internal use'
        name = args[0]
        kwargs['install_mode'] = self._get_kwarg_install_mode(kwargs)
        tg = CustomTargetHolder(build.CustomTarget(name, self.subdir, self.subproject, kwargs), self)
        self.add_target(name, tg.held_object)
        return tg