    def build_deactivate(self):
        # query environment
        old_conda_shlvl = int(os.getenv('CONDA_SHLVL', 0))
        old_conda_prefix = os.getenv('CONDA_PREFIX', None)
        if old_conda_shlvl <= 0 or old_conda_prefix is None:
            return {
                'unset_vars': (),
                'set_vars': {},
                'export_vars': {},
                'deactivate_scripts': (),
                'activate_scripts': (),
            }
        deactivate_scripts = self._get_deactivate_scripts(old_conda_prefix)

        new_conda_shlvl = old_conda_shlvl - 1
        new_path = self.pathsep_join(self._remove_prefix_from_path(old_conda_prefix))

        assert old_conda_shlvl > 0
        set_vars = {}
        if old_conda_shlvl == 1:
            # TODO: warn conda floor
            conda_prompt_modifier = ''
            unset_vars = (
                'CONDA_PREFIX',
                'CONDA_DEFAULT_ENV',
                'CONDA_PYTHON_EXE',
                'CONDA_PROMPT_MODIFIER',
            )
            export_vars = {
                'PATH': new_path,
                'CONDA_SHLVL': new_conda_shlvl,
            }
            activate_scripts = ()
        else:
            new_prefix = os.getenv('CONDA_PREFIX_%d' % new_conda_shlvl)
            conda_default_env = self._default_env(new_prefix)
            conda_prompt_modifier = self._prompt_modifier(conda_default_env)

            unset_vars = (
                'CONDA_PREFIX_%d' % new_conda_shlvl,
            )
            export_vars = {
                'PATH': new_path,
                'CONDA_SHLVL': new_conda_shlvl,
                'CONDA_PREFIX': new_prefix,
                'CONDA_DEFAULT_ENV': conda_default_env,
                'CONDA_PROMPT_MODIFIER': conda_prompt_modifier,
            }
            activate_scripts = self._get_activate_scripts(new_prefix)

        self._update_prompt(set_vars, conda_prompt_modifier)

        return {
            'unset_vars': unset_vars,
            'set_vars': set_vars,
            'export_vars': export_vars,
            'deactivate_scripts': deactivate_scripts,
            'activate_scripts': activate_scripts,
        }