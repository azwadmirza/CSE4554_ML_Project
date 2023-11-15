    def build_activate(self, env_name_or_prefix):
        if re.search(r'\\|/', env_name_or_prefix):
            prefix = expand(env_name_or_prefix)
            if not isdir(join(prefix, 'conda-meta')):
                from .exceptions import EnvironmentLocationNotFound
                raise EnvironmentLocationNotFound(prefix)
        elif env_name_or_prefix in (ROOT_ENV_NAME, 'root'):
            prefix = context.root_prefix
        else:
            prefix = locate_prefix_by_name(env_name_or_prefix)
        prefix = normpath(prefix)

        # query environment
        old_conda_shlvl = int(os.getenv('CONDA_SHLVL', 0))
        old_conda_prefix = os.getenv('CONDA_PREFIX')
        max_shlvl = context.max_shlvl

        if old_conda_prefix == prefix:
            return self.build_reactivate()
        if os.getenv('CONDA_PREFIX_%s' % (old_conda_shlvl-1)) == prefix:
            # in this case, user is attempting to activate the previous environment,
            #  i.e. step back down
            return self.build_deactivate()

        activate_scripts = self._get_activate_scripts(prefix)
        conda_default_env = self._default_env(prefix)
        conda_prompt_modifier = self._prompt_modifier(conda_default_env)

        assert 0 <= old_conda_shlvl <= max_shlvl
        set_vars = {}
        if old_conda_shlvl == 0:
            new_path = self.pathsep_join(self._add_prefix_to_path(prefix))
            export_vars = {
                'CONDA_PYTHON_EXE': self.path_conversion(sys.executable),
                'PATH': new_path,
                'CONDA_PREFIX': prefix,
                'CONDA_SHLVL': old_conda_shlvl + 1,
                'CONDA_DEFAULT_ENV': conda_default_env,
                'CONDA_PROMPT_MODIFIER': conda_prompt_modifier,
            }
            deactivate_scripts = ()
        elif old_conda_shlvl == max_shlvl:
            new_path = self.pathsep_join(self._replace_prefix_in_path(old_conda_prefix, prefix))
            export_vars = {
                'PATH': new_path,
                'CONDA_PREFIX': prefix,
                'CONDA_DEFAULT_ENV': conda_default_env,
                'CONDA_PROMPT_MODIFIER': conda_prompt_modifier,
            }
            deactivate_scripts = self._get_deactivate_scripts(old_conda_prefix)
        else:
            new_path = self.pathsep_join(self._add_prefix_to_path(prefix))
            export_vars = {
                'PATH': new_path,
                'CONDA_PREFIX': prefix,
                'CONDA_PREFIX_%d' % old_conda_shlvl: old_conda_prefix,
                'CONDA_SHLVL': old_conda_shlvl + 1,
                'CONDA_DEFAULT_ENV': conda_default_env,
                'CONDA_PROMPT_MODIFIER': conda_prompt_modifier,
            }
            deactivate_scripts = ()

        self._update_prompt(set_vars, conda_prompt_modifier)

        if on_win and self.shell == 'cmd.exe':
            import ctypes
            export_vars.update({
                "PYTHONIOENCODING": ctypes.cdll.kernel32.GetACP(),
            })

        return {
            'unset_vars': (),
            'set_vars': set_vars,
            'export_vars': export_vars,
            'deactivate_scripts': deactivate_scripts,
            'activate_scripts': activate_scripts,
        }