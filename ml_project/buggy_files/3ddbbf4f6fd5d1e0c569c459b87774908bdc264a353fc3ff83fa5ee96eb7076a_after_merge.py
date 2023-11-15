    def build_reactivate(self):
        conda_prefix = self.environ.get('CONDA_PREFIX')
        conda_shlvl = int(self.environ.get('CONDA_SHLVL', -1))
        if not conda_prefix or conda_shlvl < 1:
            # no active environment, so cannot reactivate; do nothing
            return {
                'unset_vars': (),
                'set_vars': {},
                'export_vars': {},
                'deactivate_scripts': (),
                'activate_scripts': (),
            }
        conda_default_env = self.environ.get('CONDA_DEFAULT_ENV', self._default_env(conda_prefix))
        # environment variables are set only to aid transition from conda 4.3 to conda 4.4
        return {
            'unset_vars': (),
            'set_vars': {},
            'export_vars': {
                'CONDA_SHLVL': conda_shlvl,
                'CONDA_PROMPT_MODIFIER': self._prompt_modifier(conda_default_env),
            },
            'deactivate_scripts': self._get_deactivate_scripts(conda_prefix),
            'activate_scripts': self._get_activate_scripts(conda_prefix),
        }